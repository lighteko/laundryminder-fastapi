from fastapi import FastAPI
from datetime import datetime
import databases
from dotenv import load_dotenv
import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class Machine(BaseModel):
    machine_id: int
    dorm: int
    type: int
    status: int
    started_at: Optional[datetime] = None

class Dorm(Enum): 
    AWOMEN = 0
    AMEN = 1
    BWOMEN = 2
    BMEN = 3

# class Machine(Enum):
#     WASHER = 1
#     SHOE_WASHER = -1
#     DRYER = 2
#     SHOE_DRYER = -2

class Status(Enum):
    NOT_USING = 0
    USING = 1
    DISABLED = 2

load_dotenv()
app = FastAPI()
user, password, host, port, database = (
    os.environ.get('user'),
    os.environ.get('password'),
    os.environ.get('host'),
    os.environ.get('port'),
    os.environ.get('database')
)

# Create a database URL
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
# Create a database object
database = databases.Database(DATABASE_URL)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/machine")
async def get_machines_by_dorm(dorm_id: int):
    query = f"SELECT * FROM {dorm_id} WHERE dorm = :dorm_id"
    machines = await database.fetch_all(query=query, values={"dorm_id": dorm_id})
    return "hello machines"

@app.post("/machine/")
async def create_machine(machine: Machine):
    query = f"INSERT INTO `machines` (`id`, `dorm`, `type`, `status`) VALUES ({Machine.machine_id}, {Machine.dorm}, {Machine.type}, {Machine.status});"
    database.execute(query)
    return machine

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)