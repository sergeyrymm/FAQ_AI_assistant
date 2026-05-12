import os
from collections import deque
from threading import Lock
from typing import Any, Deque, Dict, List, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

import faiss
import numpy as np
from openai import OpenAI

from .rag_index import load_index, search_similar

load_dotenv()

# ==============================================
# НАСТРОЙКА PROXYAPI.RU (вместо OpenAI)
# ==============================================

PROXYAPI_TOKEN = os.getenv("PROXYAPI_TOKEN")
if not PROXYAPI_TOKEN:
    raise RuntimeError("PROXYAPI_TOKEN is not set. Please set it in your environment or in a .env file.")

# Создаём клиент с кастомным base_url для proxyapi.ru
client = OpenAI(
    api_key=PROXYAPI_TOKEN,
    base_url="https://api.proxyapi.ru/openai/v1"  # 🟢 Главное изменение
)

app = FastAPI(title="FAQ RAG Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MAX_HISTORY_TURNS = 10


class ChatRequest(BaseModel):
    message: str
    top_k: int = 3
    session_id: str = Field(default="default", max_length=128)


class ChatResponse(BaseModel):
    answer: str
    context: List[Dict[str, Any]]


INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "faiss_index.bin")
META_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "faqs_metadata.npy")

faiss_index, metadata = load_index(INDEX_PATH, META_PATH)

_history_lock = Lock()
_chat_histories: Dict[str, Deque[Tuple[str, str]]] = {}


def _normalize_session_id(raw: str) -> str:
    s = (raw or "").strip()
    return s if s else "default"


def _snapshot_prior_turns(session_id: str) -> List[Tuple[str, str]]:
    with _history_lock:
        dq = _chat_histories.get(session_id)
        if not dq:
            return []
        return list(dq)


def _append_turn(session_id: str, question: str, answer: str) -> None:
    with _history_lock:
        if session_id not in _chat_histories:
            _chat_histories[session_id] = deque(maxlen=MAX_HISTORY_TURNS)
        _chat_histories[session_id].append((question.strip(), answer.strip()))


def embed_text(texts: List[str]) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    vectors = [d.embedding for d in response.data]
    return np.array(vectors, dtype="float32")


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message is empty")

    session_id = _normalize_session_id(req.session_id)

    query_vec = embed_text([req.message])
    similar_items = search_similar(faiss_index, metadata, query_vec, k=req.top_k)

    context_text = "\n\n".join(
        [f"Q: {item['question']}\nA: {item['answer']}" for item in similar_items]
    )

    system_prompt = (
        """Ты FAQ-ассистент компании. Отвечай кратко и по делу на русском языке.
        Стиль общения дружелюбный, профессиональный. 
        Учитывай предыдущие реплики диалога, если они помогают понять текущий вопрос. 
        Для ответа используй только предоставленный контекст. 
        Если в контексте нет нужной информации, скажи, что не уверен и предложи связаться с поддержкой.
        В конце ответа добавляй Источник: [конкретный URL из базы знаний]

Пример правильного ответа на вопрос: "Почему письмо для сброса пароля не приходит?":
 «Проверьте папку "Спам". Если его там нет, загляните в "Корзину". Затем проверьте фильтры: Настройки → Все настройки → Правила фильтрации.
Если это не помогло, свяжитесь, пожалуйста с поддержкой.
  *Источник: https://help.mail.ru/vkmail/letters/actions/trouble/move/* »
        """
    )

    prior = _snapshot_prior_turns(session_id)
    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]
    for user_q, assistant_a in prior:
        messages.append({"role": "user", "content": user_q})
        messages.append({"role": "assistant", "content": assistant_a})
    messages.append(
        {
            "role": "user",
            "content": f"Вопрос пользователя: {req.message}\n\nКонтекст FAQ:\n{context_text}",
        }
    )

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.2,
    )

    answer = completion.choices[0].message.content or ""

    _append_turn(session_id, req.message, answer)

    return ChatResponse(answer=answer, context=similar_items)


@app.get("/health")
async def health():
    return {"status": "ok"}


