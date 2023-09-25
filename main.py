from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import databases
import config as cfg 
from crud import hardware, interface
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

@app.put("/bin_info")
async def update_bin_info(info: schemas.UpdateBinInfo):
    return await interface.update_bin_info(db, info=info)

@app.get("/bid/{identifier}")
async def get_bid(identifier: str):
    return await hardware.get_bid(db, identifier=identifier)

@app.put("/calibrate")
async def calibrate(calibrate_bin: schemas.CalibrateBin):
    return await hardware.calibrate(db, calibrate_bin = calibrate_bin)

@app.post("/data")
async def post_data(data: schemas.PostData):
    return await hardware.post_data(db, data=data)

@app.put("/image")
async def update_image(update_image: schemas.UpdateImage):
    return await interface.update_image(db, update_image)

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