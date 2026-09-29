from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")

def hash(pw : str):
    return pwd_context.hash(pw)

def verify(plain_pw, hashed_pw):
    return pwd_context.verify(plain_pw, hashed_pw)  