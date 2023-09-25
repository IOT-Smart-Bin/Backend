from sqlalchemy import select
from models import Devices
async def check_bid(db, bid: int):
    query = select([Devices.c.bid]).where(Devices.c.bid == bid)
    res = await db.execute(query)
    if not res:
        return False
    return True
    