# from app.extensions import db
from app.extensions import db
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, Date, DateTime,Time
import datetime
class BaseModel(db.Model):
    __abstract__ = True
    created_day = Column(DateTime,default=datetime.datetime.now,onupdate=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    is_active = Column(Boolean, default=True)
    