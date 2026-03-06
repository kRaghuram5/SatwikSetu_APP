from fastapi import Depends, FastAPI, APIRouter, status, HTTPException
from sqlalchemy import create_engine, Column, Float, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid
from pydantic import BaseModel

engine=create_engine("postgresql://agriadmin:agriadmin%40123@localhost:5632/agri_db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()
app_v1 = APIRouter(prefix="/api/v1",tags=["v1"])


@app.on_event("startup") #this runs only once when the application starts
def startup_dp_client():
    Base.metadata.create_all(bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str

@app_v1.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user = User(name=user.name, email=user.email, password=user.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    response = UserResponse(id=str(user.id), name=user.name, email=user.email)
    return response

@app_v1.get("/users/list", status_code=status.HTTP_200_OK)
def get_users_paginated(page: int = 1, db: Session = Depends(get_db)):
    page_size = 5
    total_users = db.query(User).count()
    offset = (page - 1) * page_size
    
    db_users = db.query(User).offset(offset).limit(page_size).all()
    
    total_pages = (total_users + page_size - 1) // page_size
    
    return {
        "page": page,
        "page_size": page_size,
        "total_users": total_users,
        "total_pages": total_pages,
        "users": [{"id": str(u.id), "name": u.name, "email": u.email} for u in db_users]
    }

@app_v1.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    response = UserResponse(id=str(user.id), name=user.name, email=user.email)
    return response

@app_v1.get("/users", status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db)):
    db_users = db.query(User).all()
    return {"users": db_users}


app.include_router(app_v1)