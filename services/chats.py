from schemas import ChatCreate, ChatUpdate
from models import Chat
from .base import ServiceBase

class ChatService(ServiceBase[Chat, ChatCreate, ChatUpdate]):
    pass

chat_service = ChatService(Chat)