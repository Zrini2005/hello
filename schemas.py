from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str
class UserAuth(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    password: str
    karma_points: int
    reputation: float | None

    class Config:
        orm_mode = True

class TaskCreateRequest(BaseModel):
    description: str
    karma_cost: int
    username: str
    password: str

class TaskCreate(BaseModel):
    description: str
    karma_cost: int

class Task(BaseModel):
    id: int
    description: str
    karma_cost: int
    owner_id: int
    chosen_by_id: int | None

    class Config:
        orm_mode = True

class TaskChooseRequest(BaseModel):
    task_id: int
    username: str
    password: str

class TaskCompleteRequest(BaseModel):
    task_id: int
    username: str
    password: str
    reputation_rating: int = None
class Transaction(BaseModel):
    id: int
    timestamp: datetime
    user_id: int
    chosen_by_id: int
    task_id: int
    karma_points: int
    description: str

    class Config:
        orm_mode = True


class Reputation(BaseModel):
    id: int
    user_id: int
    task_id: int
    rating: int
    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str

class Message(BaseModel):
    sender_id: int
    receiver_id: int
    content: str

    class Config:
        orm_mode = True