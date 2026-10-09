from fastapi import APIRouter
from models.chat_models import ChatRequest, ChatResponse
from services.rag_service import chatbot

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    answer = await chatbot(request.query, request.user_id)

    return ChatResponse(
        answer=answer,
        sources=[]
    )