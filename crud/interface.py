from fastapi import HTTPException
import schemas
from sqlalchemy import select, func
from models import Devices, DevicesTags, DataPoints
from datetime import datetime

from sqlalchemy import and_

# Create a subquery to find the latest timestamp for each bid
common_bin_subquery = (
    select([func.max(DataPoints.c.timestamp).label("latest_timestamp"), DataPoints.c.bid])
    .group_by(DataPoints.c.bid)
    .alias("latest_timestamps")
)

# Left join Devices and DataPoints using the subquery to find the latest timestamp
common_bin_query = (
    select([Devices, DataPoints.c.timestamp, DataPoints.c.gas, DataPoints.c.weight, DataPoints.c.height, DataPoints.c.humidity_inside, DataPoints.c.humidity_outside])
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

async def get_tags(db, bid: int):
    query = select(DevicesTags).where(DevicesTags.c.bid == bid)
    tags_list = await db.fetch_all(query)

    return [tag["name"] for tag in tags_list]
    

async def search(db, search_criteria: schemas.SearchBin):
    search_result = []

    if len(search_criteria.name) == 0:
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
                    "height": result[DataPoints.c.height],
                    "humidity_inside": result[DataPoints.c.humidity_inside],
                    "humidity_outside": result[DataPoints.c.humidity_outside],
                }

            # Create a new dictionary with additional information
            result_with_tags = {
                "bid": result[Devices.c.bid],
                "identifier": result[Devices.c.identifier],
                "name": result[Devices.c.name],
                "image": result[Devices.c.image],
                "location": {
                    "lat": result[Devices.c.latitude],
                    "long": result[Devices.c.longitude],
                },
                "max_height": result[Devices.c.max_height],
                "last_emptied": result[Devices.c.last_emptied],
                "last_updated": result[Devices.c.last_updated],
                "tags": tag_names,
                "data_points": data_points,
            }

            search_result.append(result_with_tags)

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
                    "height": result[DataPoints.c.height],
                    "humidity_inside": result[DataPoints.c.humidity_inside],
                    "humidity_outside": result[DataPoints.c.humidity_outside],
                }

            # Create a new dictionary with additional information
            result_with_tags = {
                "bid": result[Devices.c.bid],
                "identifier": result[Devices.c.identifier],
                "name": result[Devices.c.name],
                "image": result[Devices.c.image],
                "location": {
                    "lat": result[Devices.c.latitude],
                    "long": result[Devices.c.longitude],
                },
                "max_height": result[Devices.c.max_height],
                "last_emptied": result[Devices.c.last_emptied],
                "last_updated": result[Devices.c.last_updated],
                "tags": tag_names,
                "data_points": data_points,
            }

            bin_info_list.append(result_with_tags)

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
            result_with_tags = {
                "bid": result[Devices.c.bid],
                "name": result[Devices.c.name],
                "location": {
                    "lat": result[Devices.c.latitude],
                    "long": result[Devices.c.longitude],
                },
                "tags": tag_names,
            }

            bin_location_list.append(result_with_tags)

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
        start_date = datetime.strptime(options.start_date, "%Y-%m-%d %H:%M:%S.%f")

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

        for result in results:
            # Convert the timestamp (just in case)
            timestamp = result[DataPoints.c.timestamp].strftime("%Y-%m-%d %H:%M:%S.%f")

            result_dict = {
                "timestamp": timestamp,
                "gas": result[DataPoints.c.gas],
                "weight": result[DataPoints.c.weight],
                "height": result[DataPoints.c.height],
                "humidity_inside": result[DataPoints.c.humidity_inside],
                "humidity_outside": result[DataPoints.c.humidity_outside],
            }

            data_points.append(result_dict)

    except Exception as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while executing the query.")

    return data_points




