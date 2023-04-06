from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from jsonschema import validate, ValidationError
import json

# Load user contract
with open("user_contract.json", "r") as file:
    user_contract = json.load(file)

app = FastAPI()

# SQLAlchemy setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str

@app.post("/users", response_model=UserOut)
def create_user(user: UserCreate):
    # Validate request against user contract
    try:
        validate(instance=user.dict(), schema=user_contract["request"])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Process the request and create the user
    new_user = User(name=user.name, email=user.email, password=user.password)
    session = SessionLocal()
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    session.close()

    # Return the response
    response = UserOut(id=new_user.id, name=new_user.name, email=new_user.email)
    validate(instance=response.dict(), schema=user_contract["response"])
    return response

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    session = SessionLocal()
    user = session.query(User).get(user_id)
    session.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    response = UserOut(id=user.id, name=user.name, email=user.email)
    return response