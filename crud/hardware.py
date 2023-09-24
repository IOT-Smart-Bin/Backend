from fastapi import HTTPException
import schemas
from sqlalchemy import update, select, insert
from models import Devices, DataPoints
from datetime import datetime

async def get_bid(db, identifier: str):
    query = select([Devices.c.bid]).where(Devices.c.identifier == identifier)
    res = await db.execute(query)
    if not res:
        query = insert(Devices).values(identifier=identifier, name = "", max_height = 0, last_emptied = datetime.now(), last_updated = datetime.now())
        res = await db.execute(query = query)
        # query = """INSERT INTO "Devices" (identifier, name, max_height) VALUES (:identifier, :name, :max_height)"""
        # values = {
        #     "identifier": identifier,
        #     "name":"",
        #     "max_height": 0,
        #     "last_emptied": datetime.now(),
        #     "last_updated": datetime.now()
        # }
        # res = await db.execute(query = query, values = values)
        
        # print(res)
        query = update(Devices).where(Devices.c.bid == res).values(name = f"bin_{res}")
        await db.execute(query)
        return {"bid":res}
    else:
        return {"bid": res}

async def calibrate(db, calibrate_bin:schemas.CalibrateBin):
    query = update(Devices).where(Devices.c.bid == calibrate_bin.bid).values({
        Devices.c.max_height: calibrate_bin.max_height
    })
    res = await db.execute(query = query)
    if res is not None:
        return
    else:
        raise HTTPException(status_code=404, detail={"error_code":"1", "message":"The device with the bid doesn't exist in the table"})

async def post_data(db, data:schemas.PostData):
    time = datetime.now()
    data.timestamp = time
    values = data.model_dump()
    query = insert(DataPoints).values(values)
    try:
        res = await db.execute(query = query)
    except:
        raise HTTPException(status_code=404, detail={"error_code":"1", "message":"The device with the bid doesn't exist in the table"})
    query = update(Devices).where(Devices.c.bid == data.bid).values(last_updated = time)
    res = await db.execute(query = query)
    return