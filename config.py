from dotenv import dotenv_values
import os

current_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.env") 
config = dict(dotenv_values(current_path))
DATABASE_USERNAME = config["DATABASE_USERNAME"]
DATABASE_PASSWORD = config["DATABASE_PASSWORD"]
DATABASE_HOST = config["DATABASE_URL"]
DATABASE_NAME = config["DATABASE_NAME"]