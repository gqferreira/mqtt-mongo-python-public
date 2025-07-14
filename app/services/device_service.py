from app.db import db
from pymongo.errors import PyMongoError

def get_device(channel):
	"""
	Retrieves a device document from the database by its channel.

    Args:
        channel (str): The unique identifier (channel) of the device.

    Returns:
        dict | None: The device document if found, otherwise None.
        If an exception occurs, returns a tuple (Exception, 500).
	"""
	try:
		collection = db["device"]
		result = collection.find_one({ "channel": channel })

		if result:
			print("Document found:", result)
			return result
		else:
			print("No documents found")
			return None
	except Exception as e:
		print("Error querying device:", e)
		return e, 500
    
def insert_device(device):
	"""
	Inserts or updates a device document in the database.

    If a device with the same channel already exists, it will be updated.
    Otherwise, a new device will be inserted.

    Args:
        device (dict): A dictionary containing the device's data.
            Expected keys: 'channel', 'description'.

    Returns:
        tuple:
            - bool: True if the operation was successful, False otherwise.
            - int: HTTP status code representing the result:
                - 201: Device inserted.
                - 200: Device updated.
                - 500: Database error.
	"""
	
	try:
		collection = db["device"]

		filter = { "channel": device["channel"] }
		update = {
			"$set": {
				"channel": device["channel"],
				"description": device["description"],
				"status": True
			}
		}

		result = collection.update_one(filter, update, upsert=True)

		if result.upserted_id:
			print(f"Device inserted with _id: {result.upserted_id}")
			return True, 201
		else:
			print(f"Device updated")
			return True, 200

	except PyMongoError as e:
		print("Error inserting document:", e)
		return False, 500