from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import pytz

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    karma_points = Column(Integer, default=0)
    reputation = Column(Float, default=None) 

    messages_sent = relationship("Message", back_populates="sender", foreign_keys="[Message.sender_id]")
    messages_received = relationship("Message", back_populates="receiver", foreign_keys="[Message.receiver_id]")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    karma_cost = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))
    chosen_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", foreign_keys=[owner_id])
    chosen_by = relationship("User", foreign_keys=[chosen_by_id])
class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    user_id = Column(Integer, ForeignKey("users.id"))
    chosen_by_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    
    karma_points = Column(Integer)
    description = Column(String)

    user = relationship("User", foreign_keys=[user_id])
    task = relationship("Task", foreign_keys=[task_id])
class Reputation(Base):
    __tablename__ = "reputations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    rating = Column(Integer) 
    timestamp = Column(DateTime, default=datetime.now)

    user = relationship("User", foreign_keys=[user_id])
    task = relationship("Task", foreign_keys=[task_id])

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    sender = relationship("User", back_populates="messages_sent", foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="messages_received", foreign_keys=[receiver_id])