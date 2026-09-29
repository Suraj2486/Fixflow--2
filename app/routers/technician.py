from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from app import Enum, oauth2
from app.routers.ticket import create_notification
from ..db import get_db
from .. import models, schemas, utils

router = APIRouter(prefix='/technician', tags=['Technicians'])


@router.get("/assignedticket", response_model=List[schemas.AssignedTicket], status_code=status.HTTP_200_OK)
def get_all_assigned_tickets(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    assignedTickets = db.query(models.Ticket).filter(models.Ticket.technician_id == current_user).all()

    return assignedTickets


@router.get("/newassignedticket", response_model=List[schemas.AssignedTicket], status_code=status.HTTP_200_OK)
def get_new_assigned_tickets(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    assignedTickets = db.query(models.Ticket).filter(models.Ticket.technician_id == current_user, models.Ticket.status == Enum.TicketStatus.ASSIGNED).all()

    response = assignedTickets
    for ticket in assignedTickets:
        ticket.status = Enum.TicketStatus.IN_PROGRESS
    
    db.commit()
    for ticket in assignedTickets:
        db.refresh(ticket)

    return response




@router.patch("/updateticket/{id}", status_code=status.HTTP_200_OK)
def update_ticket(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    ticket_query = db.query(models.Ticket).filter(models.Ticket.id == id, models.Ticket.technician_id == current_user, models.Ticket.status == Enum.TicketStatus.IN_PROGRESS)

    ticket = ticket_query.first()
    if ticket == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket with id: {id} was not found")
       
    ticket.status = Enum.TicketStatus.WAITING_FOR_USER


    notification = {
        'notification_for' : ticket.user_id,
        "created_by" : current_user,
        "msg_type" : Enum.MsgType.STATUS_CHANGE,
        "ticket_id" : ticket.id,
        "message" : "Ticket updated waiting_for_uh..."
    }
            
    create_notification(notification,db)
    db.commit()
    return {"msg" : "updated successfully"}

@router.get("/gettickets", status_code=status.HTTP_200_OK)
def get_ticket( priority: Optional[str] = None, ticket_status: Optional[str] = None, limit: int = 10, skip: int = 0, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    query = db.query(models.Ticket).filter(models.Ticket.technician_id == current_user)

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