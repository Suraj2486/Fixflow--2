from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app import oauth2
from ..db import get_db
from .. import models, schemas, utils
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app import db


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post("/", status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered."
        )
    user_data = user.model_dump()
    user_data["password"] = utils.hash(user.password)    
    new_user = models.User(**user_data)
    db.add(new_user)    
    db.commit()    
    db.refresh(new_user)
    
    return {f"user {new_user.email} created successfully"}


@router.post('/login', response_model = schemas.Token)
def login(user_credentials : OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db.get_db)): 
    print(1)
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    print(user)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Credentials")
    print(4)
    access_token = oauth2.c_access_token(data = {"user_id" : user.id})
    return {"access_token": access_token, "token_type": "bearer"}

    
