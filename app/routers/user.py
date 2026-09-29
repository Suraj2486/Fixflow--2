from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app import Enum, oauth2
from app.Enum import HistoryType
from app.routers.admin import ticket
from ..db import get_db
from .. import models, schemas, utils
from app import db
from app.routers.ticket import create_history, create_notification 

from app.routers import ticket

router = APIRouter(prefix='/users', tags=['Users'])


# @router.post("/createticket", status_code=status.HTTP_201_CREATED, response_model=schemas.Ticket)
# def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
#     new_ticket = models.Ticket(user_id=current_user, **ticket.model_dump())
#     db.add(new_ticket)
    
#     db.commit()
#     db.refresh(new_ticket)
#     return new_ticket

@router.post("/createticket", status_code=status.HTTP_201_CREATED, response_model=schemas.Ticket)
def create_ticket(
    ticket: schemas.TicketCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    current_user_id = int(request.state.user_id.id)
    
    new_ticket = models.Ticket(user_id=current_user_id, **ticket.model_dump())
    
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    
    return new_ticket



@router.get("/ticket/{id}", status_code=status.HTTP_200_OK)
def get_ticket(id:int,db:Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    query = db.query(models.Ticket).filter(models.Ticket.id == id)
    ticket = query.first()
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"ticket with id: {id} not found")
    if ticket.user_id != current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail =f"unauthorized for {id} ticket")
    return ticket

    
@router.get("/gettickets", status_code=status.HTTP_200_OK)
def get_ticket( priority: Optional[str] = None, ticket_status: Optional[str] = None, limit: int = 10, skip: int = 0, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    query = db.query(models.Ticket).filter(models.Ticket.user_id == current_user)

    if ticket_status is not None:
        valid_status = [Enum.TicketStatus.REPORTED, Enum.TicketStatus.ASSIGNED, Enum.TicketStatus.IN_PROGRESS, Enum.TicketStatus.WAITING_FOR_USER, Enum.TicketStatus.RESOLVED, Enum.TicketStatus.CLOSED]
        if ticket_status not in valid_status:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {ticket_status}")
        query = query.filter(models.Ticket.status == ticket_status)

    if priority is not None:
        valid_priority = [Enum.TicketPriority.MEDIUM, Enum.TicketPriority.HIGH, Enum.TicketPriority.LOW, Enum.TicketPriority.CRITICAL]
        if priority not in valid_priority:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {priority}")
        query = query.filter(models.Ticket.priority == priority)

    tickets = query.offset(skip).limit(limit).all()
    return tickets

@router.patch("/confirmresolve/{id}", status_code=status.HTTP_200_OK)
def comfirm_ticket(id:int,db:Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    query = db.query(models.Ticket).filter(models.Ticket.id == id)
    ticket = query.first()
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"ticket with id: {id} not found")
    if ticket.user_id != current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail =f"unauthorized for {id} ticket")
    if ticket.status != Enum.TicketStatus.WAITING_FOR_USER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = f"it is not in waiting_for_user status..")

    
    history = {
        "user_id": current_user,  
        "ticket_id": ticket.id,   
        "change_type": Enum.HistoryType.STATUS,
        "old_value": ticket.status,
        "new_value": Enum.TicketStatus.RESOLVED
    }

    notification = {
        'notification_for' : ticket.user_id,
        "created_by" : current_user,
        "msg_type" : Enum.MsgType.STATUS_CHANGE,
        "ticket_id" : ticket.id,
        "message" : "Ticket Resolved..."
    }
                
    create_notification(notification,db)
    create_history(history, db)
    ticket.status = Enum.TicketStatus.RESOLVED
    db.commit()
    return {"msg" : "updated successfully"}