from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from app import Enum, oauth2
from app.Enum import HistoryType, MsgType
from ..db import get_db
from .. import models, schemas, utils
from app import db

router = APIRouter(prefix='/ticket', tags=['ticket'])


def create_history(ticket: schemas.HistoryCreate, db: Session = Depends(get_db)):
    new_history = models.TicketHistory(
        user_id=ticket["user_id"],
        ticket_id=ticket["ticket_id"],
        change_type=ticket["change_type"],
        old_value=str(ticket["old_value"]) if ticket["old_value"] is not None else None,
        new_value=str(ticket["new_value"]) if ticket["new_value"] is not None else None
    )
    db.add(new_history)

def create_notification(notification:schemas.Notification, db:Session=Depends(get_db)):
    new_notification = models.Notification(
        notification_for=notification['notification_for'],
        ticket_id = notification['ticket_id'],
        message = notification['message'],
        msg_type = notification['msg_type'],
        created_by = notification['created_by']
    )
    db.add(new_notification)



@router.get("/history/{id}")
def get_history(id:int, db: Session = Depends(get_db)):
    ticket = db.query(models.TicketHistory).filter(models.TicketHistory.ticket_id == id).all()
    return ticket