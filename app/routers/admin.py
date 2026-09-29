from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

from app import Enum, oauth2
from ..db import get_db
from .. import models, schemas, utils

router = APIRouter(prefix='/admin', tags=['Admin'])

def roleChecker(current_user: models.User = Depends(oauth2.get_user)):
    allowed_roles = [Enum.UserRole.ADMIN] 
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    return current_user.id



@router.patch("/assignrole", status_code=status.HTTP_202_ACCEPTED)
def assign_role(assignrole: schemas.AssignRole, db: Session = Depends(get_db), current_user: int = Depends(roleChecker)):
    user_query = db.query(models.User).filter(models.User.id == assignrole.user_id)
    user = user_query.first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ticket with id: {assignrole.ticket_id} was not found")

    user.role = assignrole.role    
    db.commit()
    return "Updated successfully"



@router.get("/tickets", status_code=status.HTTP_200_OK)
def ticket(db: Session = Depends(get_db), current_user: int = Depends(roleChecker)):
    tickets = db.query(models.Ticket).all()
    return tickets


@router.get("/user", status_code=status.HTTP_200_OK,response_model=List[schemas.GetUser])
def user(db: Session = Depends(get_db), current_user: int = Depends(roleChecker)):
    users = db.query(models.User).all()
    return users



