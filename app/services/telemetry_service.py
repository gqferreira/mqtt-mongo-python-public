from pymongo import MongoClient
from bson.son import SON
from app.db import db
from pymongo.errors import PyMongoError
from bson import ObjectId, DBRef
from datetime import datetime, UTC
import app.config as config

def insert_telemetry(telemetry, device):
	"""
    Inserts a new telemetry record into the database.

    Each telemetry record is associated with a device reference.
    The timestamp is automatically added using the current UTC time.

    Args:
        telemetry (dict): A dictionary containing telemetry values.
            Expected keys: 'light', 'temperature'.
        device (dict): A dictionary representing the related device document.
            Must contain the '_id' field.

    Returns:
        None
        Logs success or prints an error message in case of a database failure.
	"""
      
	try:
		collection = db["telemetry"]

		document = {
			"date": datetime.now(UTC),
			"light": telemetry["light"],
			"temperature": telemetry["temperature"],
			"device": DBRef(collection="device", id=ObjectId(device['_id']), database=config.MONGODB_DB)
		}
            
		collection.insert_one(document)
		print("Document inserted")
	except PyMongoError as e:
		print("Error inserting document:", e)

def list_telemetry(channel=None):
    """
    Retrieves the latest 100 telemetry records from the database.

    Optionally filters the results by device channel.
    Only devices with 'status': True are included.

    Args:
        channel (str, optional): The channel identifier of the device to filter by.
            If not provided, returns records for all active devices.

    Returns:
        tuple:
            - list: A list of telemetry records with formatted date and device info.
            - int: HTTP status code.
                - 200: Success.
                - 500: Internal server error.
    """
    try:
        collection = db['telemetry']
        
        pipeline = [
            {
                "$lookup": {
                    "from": "device",
                    "localField": "device.$id",
                    "foreignField": "_id",
                    "as": "device"
                }
            }
        ]

        if channel:
            pipeline.append({ "$match": { "device.channel": channel } })

        pipeline += [
            { "$unwind": "$device" },
            { "$match": { "device.status": True } },
            { "$sort": { "date": -1 } },
            {
                "$project": {
                    "_id": False,
                    "date": {
                        "$dateToString": {
                            "format": "%H:%M:%S %d/%m/%Y",
                            "date": "$date",
                            "timezone": "-03:00"
                        }
                    },
                    "light": 1,
                    "temperature": 1,
                    "channel": "$device.channel",
                    "description": "$device.description"
                }
            },
            { "$limit": 100 }
        ]

        return list(collection.aggregate(pipeline)), 200
    except Exception as e:
        print("Error querying telemetry:", e)
        return e, 500