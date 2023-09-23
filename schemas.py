from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# search >> list of bininfo w/ everthing (latest data point)

# getBinInfo >> input list[bid] >> list[binInfo]
# getBinHistory >> start-date, bid >> binInfo + list[dataPoint] initialization


class Location(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DataPoint(BaseModel):
    timestamp: datetime
    gas: float
    weight: float
    capacity: int
    humidity_inside: float
    humidity_outside: float

    class Config:
        orm_mode = True


class BinInfo(DataPoint):
    bid: int
    identifier: str
    tags: list[str]
    name: str
    last_emptied: datetime
    last_updated: datetime
    location: Location
    image: Optional[str] = None


class BinMapInfo(BaseModel):
    bid: int
    name: str
    tags: list[str]
    location: Location


class SearchBin(BaseModel):
    name: Optional[str] = None
    tag: Optional[list[str]] = None


class GetBinHistories(BaseModel):
    bid: int
    start_date: datetime


class UpdateBinInfo(BaseModel):
    bid: int
    location: Optional[Location]
    name: str
    tags: list[str]


class CalibrateBin(BaseModel):
    identifier: str
    max_height: float


class UpdateImage(BaseModel):
    bid: int
    image: str


class PostBinData(DataPoint):
    bid: int
    gas: float
    weight: float
    height: float
    humidity_inside: float
    humidity_outside: float
