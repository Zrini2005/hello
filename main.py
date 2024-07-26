from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas,datetime
from typing import List
from datetime import datetime
from database import SessionLocal, engine
import pytz
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = models.User(username=user.username, password=user.password, karma_points=500)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
@app.post("/users/login", response_model=schemas.User)
def login_user(user: schemas.UserAuth, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user is None or db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return db_user

@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreateRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == task.username).first()
    if db_user is None or db_user.password != task.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    if db_user.karma_points < task.karma_cost:
        raise HTTPException(status_code=400, detail="Insufficient karma points")
    
    new_task = models.Task(description=task.description, karma_cost=task.karma_cost, owner_id=db_user.id)
    db_user.karma_points -= task.karma_cost
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    db.refresh(db_user)
    return new_task

@app.post("/tasks/choose", response_model=schemas.Task)
def choose_task(request: schemas.TaskChooseRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == request.username).first()
    if db_user is None or db_user.password != request.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    task = db.query(models.Task).filter(models.Task.id == request.task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.chosen_by_id is not None:
        raise HTTPException(status_code=400, detail="Task already chosen")
    
    task.chosen_by_id = db_user.id
    db.commit()
    db.refresh(task)
    return task

@app.post("/tasks/complete", response_model=schemas.Task)
def complete_task(request: schemas.TaskCompleteRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == request.username).first()
    if db_user is None or db_user.password != request.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    task = db.query(models.Task).filter(models.Task.id == request.task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.owner_id != db_user.id:
        raise HTTPException(status_code=400, detail="Only the task owner can mark it as complete")
    
    if task.chosen_by_id is None:
        raise HTTPException(status_code=400, detail="Task has not been chosen yet")
    transaction = models.Transaction(
            task_id=task.id,
            user_id=task.owner_id,
            chosen_by_id = task.chosen_by_id, 
            karma_points=task.karma_cost,
        
            description=task.description,
        
            timestamp = datetime.now(pytz.timezone('Asia/Kolkata'))
        )
    db.add(transaction)
    reputation = models.Reputation(
        user_id=task.chosen_by_id,
        task_id=task.id,
        rating=request.reputation_rating  
    )
    db.add(reputation)
    db.commit()
    
    chosen_user = db.query(models.User).filter(models.User.id == task.chosen_by_id).first()
    reputations = db.query(models.Reputation).filter(models.Reputation.user_id == chosen_user.id).all()
    ratings = [r.rating for r in reputations if r.rating is not None]
    if ratings:
        avg_reputation = sum(ratings) / len(ratings)
    else:
        avg_reputation = None
    chosen_user.reputation = avg_reputation
    chosen_user.karma_points += task.karma_cost
    db.delete(task)
    db.commit()
    db.refresh(chosen_user)
    return task

@app.get("/tasks/all")
def get_all_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks

@app.post("/transactions/history", response_model=List[schemas.Transaction])
def get_transaction_history(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    transactions = db.query(models.Transaction).filter((models.Transaction.user_id == user.id) | (models.Transaction.chosen_by_id == user.id)).all()
    return transactions

@app.post("/messages/", response_model=schemas.Message)
def send_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    sender = db.query(models.User).filter(models.User.id == message.sender_id).first()
    receiver = db.query(models.User).filter(models.User.id == message.receiver_id).first()

    if sender is None or receiver is None:
        raise HTTPException(status_code=404, detail="User not found")

    new_message = models.Message(sender_id=sender.id, receiver_id=receiver.id, content=message.content)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@app.get("/messages/{user_id}/{other_user_id}", response_model=List[schemas.Message])
def get_messages(user_id: int, other_user_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(
        ((models.Message.sender_id == user_id) & (models.Message.receiver_id == other_user_id)) |
        ((models.Message.sender_id == other_user_id) & (models.Message.receiver_id == user_id))
    ).all()
    return messages

@app.get("/messages/{user_id}", response_model=List[schemas.Message])
def get_messages(user_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(
        (models.Message.sender_id == user_id) |
        (models.Message.receiver_id == user_id)
    ).all()
    return messages




    