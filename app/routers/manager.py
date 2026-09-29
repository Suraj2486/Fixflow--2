from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from app import Enum, oauth2
from app.models import Notification
from ..db import get_db
from .. import models, schemas, utils
from app import db
from app import schemas
from app.routers.ticket import create_history, create_notification


router = APIRouter(prefix='/manager', tags=['Manager'])



def roleChecker(current_user: models.User = Depends(oauth2.get_user)):
    allowed_roles = [Enum.UserRole.MANAGER, Enum.UserRole.ADMIN] 
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    return current_user.id

@router.patch("/assignticket", status_code=status.HTTP_202_ACCEPTED)
def assign_ticket(assignticket: schemas.AssignTicket, db: Session = Depends(get_db), current_user: int = Depends(roleChecker)):
    ticket_query = db.query(models.Ticket).filter(models.Ticket.id == assignticket.ticket_id)
    ticket = ticket_query.first()
    if ticket == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket with id: {assignticket.ticket_id} was not found")

    technician = db.query(models.User).filter(models.User.id == assignticket.technician_id).first()
    if technician == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"technician with id: {assignticket.technician_id} was not found")

    ticket.status = Enum.TicketStatus.ASSIGNED
    ticket.technician_id = assignticket.technician_id

    history = {
        "user_id": current_user,  
        "ticket_id": ticket.id,   
        "change_type": Enum.HistoryType.ASSIGNED_TECHNICIAN,
        "old_value": None,
        "new_value": assignticket.technician_id
    }
    #   notification_for : int
    #     ticket_id : int
    #     message : str
    #     msg_type : MsgType
    #     created_by : int
    notification = {
        'notification_for' : ticket.user_id,
        "created_by" : current_user,
        "msg_type" : Enum.MsgType.ASSIGNEMNT,
        "ticket_id" : ticket.id,
        "message" : "Ticket Assigned to Technician..."
    }
    
    create_notification(notification,db)

    create_history(history, db)
    db.commit()
    return "Updated successfully"



@router.patch("/changepriority/{id}", status_code=status.HTTP_200_OK)
def change(id:int,  payload: schemas.PriorityUpdate, db: Session = Depends(get_db), current_user: int = Depends(roleChecker)):

    ticket_query = db.query(models.Ticket).filter(models.Ticket.id == id)
    ticket = ticket_query.first()
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket with id: {id} was not found")

    ValidPriority = [Enum.TicketPriority.HIGH, Enum.TicketPriority.MEDIUM, Enum.TicketPriority.LOW]

    if payload.priority not in ValidPriority:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"invalid priority {payload.priority}")


    history = {
        "user_id": current_user,  
        "ticket_id": ticket.id,   
        "change_type": Enum.HistoryType.PRIORITY,
        "old_value": ticket.priority,
        "new_value": payload.priority
    }

    create_history(history, db)
    ticket.priority = payload.priority
    db.commit()

    return {"message": "Updated successfully"}


@router.get("/gettickets", status_code=status.HTTP_200_OK)
def get_all_ticket(technician_id :Optional[int]=None, priority: Optional[str] = None, ticket_status: Optional[str] = None, limit: int = 10, skip: int = 0, db: Session = Depends(get_db), current_user: int = Depends(roleChecker)):

    query = db.query(models.Ticket).all()

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

    if technician_id is not None:
        query = query.filter(models.Ticket.technician_id == technician_id)
    tickets = query.offset(skip).limit(limit).all()
    return tickets

@router.post("/createcategory",  status_code=status.HTTP_201_CREATED)
def createCategory(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: int = Depends(roleChecker)):
    category = models.Category(name = category.name)
    db.add(category)
    db.commit()
    return "created successfully"

@router.patch("/changestatus/{id}", status_code=status.HTTP_200_OK)
def changeStatus(id:int, newstatus:schemas.StatusChange, db: Session = Depends(get_db), current_user: int = Depends(roleChecker)):
    ticket_query = db.query(models.Ticket).filter(models.Ticket.id == id)
    if ticket_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket with id: {id} was not found")
    ticket = ticket_query.first()

    notification = {
            'notification_for' : ticket.user_id,
            "created_by" : current_user,
            "msg_type" : Enum.MsgType.STATUS_CHANGE,
            "ticket_id" : ticket.id,
            "message" : "Ticket's status is changed..."
        }
    history = {
            "user_id": current_user,  
            "ticket_id": ticket.id,   
            "change_type": Enum.HistoryType.STATUS,
            "old_value": ticket.status,
            "new_value": newstatus.status
        }      
    ticket.status = newstatus.status

    create_history(history, db)
    create_notification(notification,db)
    db.commit()
    return "updated successfully"