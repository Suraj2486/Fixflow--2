import app
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.routers import admin, auth, manager, technician, user, ticket
from . import db , oauth2
from .oauth2 import verify_access_token

app = FastAPI()

db.Base.metadata.create_all(bind=db.engine)


@app.middleware("http")
async def global_auth_middleware(request: Request, call_next):

    PUBLIC_PATHS = ["/auth/login"]
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    

    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing or invalid Authorization header structure. Must be 'Bearer <token>'"}
        )
    

    token = auth_header.split(" ")[1]
    
    user = verify_access_token(token, status.HTTP_401_UNAUTHORIZED)
    request.state.user_id = user 
    
    
    request.state.user = user
    
    response = await call_next(request)
    return response


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(manager.router)
app.include_router(admin.router)
app.include_router(technician.router)
app.include_router(ticket.router)


@app.get("/")
def root():
    return {"msg": "Hello Naina"}

@app.get("/dashboard")
async def dashboard(request: Request):
    current_user = request.state.user
    return {"message": f"Welcome {current_user} to your secure dashboard!"}
