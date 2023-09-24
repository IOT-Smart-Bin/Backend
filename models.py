from sqlalchemy.orm import declarative_base
import sqlalchemy

metadata = sqlalchemy.MetaData()
Base = declarative_base

Devices = sqlalchemy.Table(
    "Devices",
    metadata,
    sqlalchemy.Column("bid", sqlalchemy.Integer, primary_key = True, autoincrement = True),
    sqlalchemy.Column("identifier", sqlalchemy.Text, unique = True, nullable = False),
    sqlalchemy.Column("name", sqlalchemy.Text, nullable = False),
    sqlalchemy.Column("image", sqlalchemy.Text),
    sqlalchemy.Column("latitude", sqlalchemy.Float),
    sqlalchemy.Column("longitude", sqlalchemy.Float),
    sqlalchemy.Column("max_height", sqlalchemy.Float, nullable = False),
    sqlalchemy.Column("last_emptied", sqlalchemy.DateTime, nullable = False),
    sqlalchemy.Column("last_updated", sqlalchemy.DateTime, nullable = False)
)

DataPoints = sqlalchemy.Table(
    "DataPoints",
    metadata,
    sqlalchemy.Column("bid", sqlalchemy.Integer, sqlalchemy.ForeignKey("Devices.bid", ondelete='CASCADE'), primary_key = True),
    sqlalchemy.Column("timestamp", sqlalchemy.DateTime, primary_key = True),
    sqlalchemy.Column("gas", sqlalchemy.Float, nullable = False),
    sqlalchemy.Column("weight", sqlalchemy.Float, nullable = False),
    sqlalchemy.Column("height", sqlalchemy.Float, nullable = False),
    sqlalchemy.Column("humidity_inside", sqlalchemy.Float, nullable = False),
    sqlalchemy.Column("humidity_outside", sqlalchemy.Float, nullable = False),
)

Tags = sqlalchemy.Table(
    "Tags",
    metadata,
    sqlalchemy.Column("name", sqlalchemy.Text, primary_key = True),
)

DevicesTags = sqlalchemy.Table(
    "DevicesTags",
    metadata,
    sqlalchemy.Column("bid", sqlalchemy.Integer, sqlalchemy.ForeignKey("Devices.bid", ondelete="CASCADE"), primary_key = True),
    sqlalchemy.Column("name", sqlalchemy.Text, sqlalchemy.ForeignKey("Tags.name", onupdate="CASCADE", ondelete="CASCADE"),primary_key = True),
)