from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
   
    nivel_cunostinte = Column(String, default="Incepator") 
    
    
    roadmaps = relationship("Roadmap", back_populates="user")
    attempts = relationship("UserAttempt", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")


class Roadmap(Base):
    __tablename__ = 'roadmaps'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    obiectiv = Column(String, nullable=False)
   
    plan_json = Column(JSON, nullable=False) 
    
    user = relationship("User", back_populates="roadmaps")


class UserAttempt(Base):
    __tablename__ = 'user_attempts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    problema_id = Column(String, nullable=False)

    cod_trimis = Column(Text, nullable=False) 
    
    status = Column(String, nullable=False) 
    timp_executie = Column(Float)
    memorie_consumata = Column(Float)
    
    user = relationship("User", back_populates="attempts")


class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    mesaj_user = Column(Text, nullable=False)
    raspuns_tutor = Column(Text, nullable=False)
    
    proces_cot_json = Column(JSON, nullable=True) 
    
    user = relationship("User", back_populates="conversations")


class Favorite(Base):
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    titlu_teorie = Column(String, nullable=False) 
    sursa_chromadb = Column(String, nullable=False)
    
    user = relationship("User", back_populates="favorites")


DATABASE_URL = "postgresql://postgres:biania13@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)

if __name__ == "__main__":
    print("Se creeaza tabelele in baza de date...")
    
    Base.metadata.create_all(engine)
    print("Tabelele au fost create cu succes! 🚀")