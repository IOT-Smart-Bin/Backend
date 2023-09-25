from fastapi import HTTPException
import schemas
from sqlalchemy import update, delete
from sqlalchemy.dialects.postgresql import insert
from models import Devices, DevicesTags, Tags
from functions import check_bid
import boto3
import base64
from io import BytesIO
import imghdr

async def update_bin_info(db, info:schemas.UpdateBinInfo):
    bid = info.bid
    res = await check_bid(db, bid) # Return False if BID doesn't exist
    if not res:
        raise HTTPException(status_code=404, detail={"error_code":"1", "message":"The device with the bid doesn't exist in the table"})
    
    query = update(Devices).where(Devices.c.bid == bid).values({
        "name": info.name,
        "latitude": info.location.latitude,
        "longitude": info.location.longitude
    })
    await db.execute(query)
    tags = [{"name":tag} for tag in info.tags]
    query = insert(Tags).values(tags).on_conflict_do_nothing()
    await db.execute(query)
    query = delete(DevicesTags).where(DevicesTags.c.bid == bid)
    await db.execute(query)
    tags = [{"bid":bid,"name":tag} for tag in info.tags]
    query = insert(DevicesTags).values(tags).on_conflict_do_nothing()
    await db.execute(query)


async def update_image(db, updated_image: schemas.UpdateImage):
    res = await check_bid(db, updated_image.bid)
    if not res:
        raise HTTPException(status_code=404, detail={"error_code":"1", "message":"The device with the bid doesn't exist in the table"})
    bucket_name = 'smartbinbucket-ice'
    binary_data = base64.b64decode(updated_image.image)
    image_stream = BytesIO(binary_data)
    image_format = imghdr.what(None, h=binary_data)
    if image_format:
        object_key = f"bin_{updated_image.bid}_image.{image_format}"
    else:
        raise HTTPException(status_code=400, detail={"error_code":"2","message":"Unknown file extension"})
    # print(binary_data)
    s3 = boto3.client('s3')
    s3.put_object(Bucket = bucket_name, Key = object_key, Body = image_stream)
    image_url = "https://smartbinbucket-ice.s3.ap-southeast-1.amazonaws.com/"+object_key
    print(image_url)
    query = update(Devices).where(Devices.c.bid == updated_image.bid).values({
        "image": image_url
    })
    await db.execute(query)
    return