from fastapi import HTTPException
import schemas
from sqlalchemy import update, delete, select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import and_
from models import Devices, DevicesTags, Tags, DataPoints
from datetime import datetime
from functions import check_bid
import boto3
import base64
from io import BytesIO
import imghdr

common_bin_subquery = (
    select([func.max(DataPoints.c.timestamp).label("latest_timestamp"), DataPoints.c.bid])
    .group_by(DataPoints.c.bid)
    .alias("latest_timestamps")
)

common_bin_query = (
    select([Devices, DataPoints.c.timestamp, DataPoints.c.gas, DataPoints.c.weight, DataPoints.c.height, DataPoints.c.humidity_inside, DataPoints.c.humidity_outside, DataPoints.c.temperature])
    .outerjoin(
        common_bin_subquery,
        common_bin_subquery.c.bid == Devices.c.bid,
    )
    .outerjoin(
        DataPoints,
        and_(
            DataPoints.c.bid == Devices.c.bid,
            DataPoints.c.timestamp == common_bin_subquery.c.latest_timestamp,
        ),
    )
)

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
    query = delete(DevicesTags).where(DevicesTags.c.bid == bid)
    await db.execute(query)
    if info.tags is not None:
        tags = [{"name":tag} for tag in info.tags]
        query = insert(Tags).values(tags).on_conflict_do_nothing()
        await db.execute(query)
        tags = [{"bid":bid,"name":tag} for tag in info.tags]
        query = insert(DevicesTags).values(tags).on_conflict_do_nothing()
        await db.execute(query)

async def update_image(db, updated_image: schemas.UpdateImage):
    image = updated_image.image.split(',')[1]
    res = await check_bid(db, updated_image.bid)
    if not res:
        raise HTTPException(status_code=404, detail={"error_code":"1", "message":"The device with the bid doesn't exist in the table"})
    bucket_name = 'smartbinbucket-ice'
    binary_data = base64.b64decode(image)
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


async def get_tags(db, bid: int):
    query = select(DevicesTags).where(DevicesTags.c.bid == bid)
    tags_list = await db.fetch_all(query)

    return [tag["name"] for tag in tags_list]
    
async def search(db, search_criteria: schemas.SearchBin):
    search_result = []

    if search_criteria.name is None or len(search_criteria.name) == 0:
        return search_result

    try:
        query = common_bin_query.where(Devices.c.name.ilike(f"%{search_criteria.name}%"))
        results = await db.fetch_all(query)

        for result in results:
            tag_names = await get_tags(db, result[Devices.c.bid])

            # Check if there are no corresponding entries in DataPoints
            if result[DataPoints.c.timestamp] is None:
                data_points = None
            else:
                data_points = {
                    "timestamp": result[DataPoints.c.timestamp],
                    "gas": result[DataPoints.c.gas],
                    "weight": result[DataPoints.c.weight],
                    "capacity": int(result[DataPoints.c.height] / result[Devices.c.max_height] * 100),
                    "humidity_inside": result[DataPoints.c.humidity_inside],
                    "humidity_outside": result[DataPoints.c.humidity_outside],
                    "temperature": result[DataPoints.c.temperature]
                }

            # Create a new dictionary with additional information
            bin_info = {
                "bid": result[Devices.c.bid],
                "name": result[Devices.c.name],
                "image": result[Devices.c.image],
                "location": {
                    "latitude": result[Devices.c.latitude],
                    "longitude": result[Devices.c.longitude],
                },
                "last_emptied": result[Devices.c.last_emptied],
                "last_updated": result[Devices.c.last_updated],
                "tags": tag_names,
                "latest_data_point": data_points
            }

            search_result.append(schemas.BinInfo(**bin_info))

    except Exception as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while executing the query.")

    return search_result

async def bins(db, bid_list: list[int]):
    bin_info_list = []

    if len(bid_list) == 0:
        return bin_info_list

    try:
        query = common_bin_query.where(Devices.c.bid.in_(bid_list))
        results = await db.fetch_all(query)

        for result in results:
            tag_names = await get_tags(db, result[Devices.c.bid])

            # Check if there are no corresponding entries in DataPoints
            if result[DataPoints.c.timestamp] is None:
                data_points = None
            else:
                data_points = {
                    "timestamp": result[DataPoints.c.timestamp],
                    "gas": result[DataPoints.c.gas],
                    "weight": result[DataPoints.c.weight],
                    "capacity": int(result[DataPoints.c.height] / result[Devices.c.max_height] * 100),
                    "humidity_inside": result[DataPoints.c.humidity_inside],
                    "humidity_outside": result[DataPoints.c.humidity_outside],
                    "temperature": result[DataPoints.c.temperature]
                }

            # Create a new dictionary with additional information
            bin_info = {
                "bid": result[Devices.c.bid],
                "name": result[Devices.c.name],
                "image": result[Devices.c.image],
                "location": {
                    "latitude": result[Devices.c.latitude],
                    "longitude": result[Devices.c.longitude],
                },
                "last_emptied": result[Devices.c.last_emptied],
                "last_updated": result[Devices.c.last_updated],
                "tags": tag_names,
                "latest_data_point": data_points
            }

            bin_info_list.append(schemas.BinInfo(**bin_info))

    except Exception as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while executing the query.")

    return bin_info_list

async def locations(db, bid_list: list[int]):
    bin_location_list = []

    if len(bid_list) == 0:
        return bin_location_list

    try:
        query = select(Devices).where(Devices.c.bid.in_(bid_list))
        results = await db.fetch_all(query)

        for result in results:
            tag_names = await get_tags(db, result[Devices.c.bid])

            # Create a new dictionary with additional information
            result_dict = {
                "bid": result[Devices.c.bid],
                "name": result[Devices.c.name],
                "location": {
                    "latitude": result[Devices.c.latitude],
                    "longitude": result[Devices.c.longitude],
                },
                "tags": tag_names,
            }

            bin_location_list.append(schemas.BinMapInfo(**result_dict))

    except Exception as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while executing the query.")

    return bin_location_list

async def histories(db, options: schemas.GetBinHistories):
    data_points = []

    if options.bid is None or options.start_date is None:
        return data_points

    try:
        # Convert the start_date ISO string to a datetime object
        start_date = options.start_date

        # Get the current datetime
        current_datetime = datetime.now()

        # Create the query to retrieve data from DataPoints
        query = (
            select([DataPoints])
            .where(
                and_(
                    DataPoints.c.bid == options.bid,
                    DataPoints.c.timestamp >= start_date,
                    DataPoints.c.timestamp <= current_datetime,
                )
            )
        )

        results = await db.fetch_all(query)

        query = select(Devices).where(Devices.c.bid == options.bid)
        bin_info_results = await db.fetch_one(query)

        for result in results:
            result_dict = {
                "timestamp": result[DataPoints.c.timestamp],
                "gas": result[DataPoints.c.gas],
                "weight": result[DataPoints.c.weight],
                "capacity": int(result[DataPoints.c.height] / bin_info_results[Devices.c.max_height] * 100),
                "humidity_inside": result[DataPoints.c.humidity_inside],
                "humidity_outside": result[DataPoints.c.humidity_outside],
                "temperature": result[DataPoints.c.temperature]
            }

            data_points.append(schemas.DataPoint(**result_dict))

    except Exception as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while executing the query.")

    return data_points





