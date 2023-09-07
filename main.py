from fastapi import FastAPI, HTTPException
from datetime import datetime
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()

load_dotenv()
app = FastAPI()
user, password, host, port, database = (
    os.environ.get('DATABASE_USER'),
    os.environ.get('DATABASE_PASSWORD'),
    os.environ.get('DATABASE_HOST'),
    os.environ.get('DATABASE_PORT'),
    os.environ.get('DATABASE_NAME')
)

# Create a database URL
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Machine(Base):
    __tablename__ = "machines"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    code = Column(Integer, index=True, nullable=False)
    dorm = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    started_at = Column(DateTime)

Base.metadata.create_all(bind=engine)

class MachineCreate(BaseModel):
    code: int
    dorm: int
    type: int
    status: int

class MachineUpdate(BaseModel):
    status: int
    started_at: datetime

@app.get("/")
def runner():
    return "api running"

@app.get("/machines/{dorm_id}")
def get_machines_by_dorm(dorm_id: int):
    db = SessionLocal()
    machines = db.query(Machine).filter(Machine.dorm == dorm_id).all()
    db.close()
    if machines is None:
        raise HTTPException(status_code=404, detail="machine not found")
    return machines

@app.get("/machines")
def get_machines_by_dorm():
    db = SessionLocal()
    machines = db.query(Machine).all()
    db.close()
    if machines is None:
        raise HTTPException(status_code=404, detail="machine not found")
    return machines

@app.post("/machines/")
def create_machine(machine: MachineCreate):
    db_machine = Machine(**machine.model_dump())
    db = SessionLocal()
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    db.close()
    return db_machine

@app.patch("/machines/{machine_id}")
def update_machine(machine_id: int, machine_update: MachineUpdate):
    db = SessionLocal()
    db_machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if db_machine is None:
        db.close()
        raise HTTPException(status_code=404, detail="machine not found")
    for field, value in machine_update.dict(exclude_unset=True).items():
        setattr(db_machine, field, value)
    db.commit()
    db.refresh(db_machine)
    db.close()
    return db_machine

@app.delete("/machines/{machine_id}")
def delete_machine(machine_id: int):
    db = SessionLocal()
    db_machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if db_machine is None:
        db.close()
        raise HTTPException(status_code=404, detail="Machine not found")
    db.delete(db_machine)
    db.commit()
    db.close()
    return machine_id

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)