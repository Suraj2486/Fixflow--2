from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from app import Enum
from app.Enum import HistoryType, MsgType

class UserCreate(BaseModel):
    email : EmailStr
    password : str
    name : str
    # role : Optional[str] = 'ADMIN'


class Token(BaseModel):
    access_token : str
    token_type : str


class TicketCreate(BaseModel):
    title : str
    description : str
    location : str
    priority : Optional[str] =  None
    category_id : int


class Ticket(TicketCreate):
    pass

class TokenData(BaseModel):
    id : Optional[str] = None
    
class AssignTicket(BaseModel):
    ticket_id : int
    technician_id : int

class AssignRole(BaseModel):
    user_id : int
    role : str
    description : str

class AssignedTicket(BaseModel):
    title: str
    description: str
    priority: str
    location: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        # Pydantic v1: allows reading SQLAlchemy attributes instead of just dictionaries
        orm_mode = True
 

class GetUser(BaseModel):
    name : str
    email : EmailStr
    role : str

class PriorityUpdate(BaseModel):
    priority: str


class CategoryCreate(BaseModel):
    name: str


class HistoryCreate(BaseModel):
    user_id : int
    ticket_id : int
    change_type : HistoryType
    old_value : str
    new_value : str


class Notification(BaseModel):
    notification_for : int
    ticket_id : int
    message : str
    msg_type : MsgType
    created_by : int


class StatusChange(BaseModel):
    status : Enum.TicketStatus