from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import databases
import config as cfg 
from crud import interface
import schemas

DATABASE_URL = f"postgresql://{cfg.DATABASE_USERNAME}:{cfg.DATABASE_PASSWORD}@{cfg.DATABASE_HOST}:5432/{cfg.DATABASE_NAME}"
db = databases.Database(DATABASE_URL)


app = FastAPI(title="REST API")
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
)

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@app.get("/")
async def root():
    return {"message": "Unused route"}

@app.post("/search")
async def search_bins(search_criteria: schemas.SearchBin):
    return await interface.search(db, search_criteria)

@app.post("/bins")
async def search_bins(bid_list: list[int]):
    return await interface.bins(db, bid_list)

@app.post("/locations")
async def search_bins(bid_list: list[int]):
    return await interface.locations(db, bid_list)

@app.post("/histories")
async def search_bins(bin_info: schemas.GetBinHistories):
    return await interface.histories(db, bin_info)