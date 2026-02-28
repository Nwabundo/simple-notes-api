from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


# -------------------------
# User Model
# -------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationship: One user -> Many notes
    notes = relationship("Note", back_populates="owner", cascade="all, delete")


# -------------------------
# Note Model
# -------------------------
class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationship back to User
    owner = relationship("User", back_populates="notes")
