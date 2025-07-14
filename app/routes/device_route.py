from flask import Blueprint, request, jsonify
from app.services.device_service import insert_device
from pydantic import BaseModel, ValidationError

class DeviceSchema(BaseModel):
    channel: str
    description: str

device_bp = Blueprint('device', __name__, url_prefix='/device')
@device_bp.route('', methods=['POST'])
def post_device():
	"""
	Inserts or updates a device in the database.

    Expects a JSON payload containing the device data. The data is validated using `DeviceSchema`.
    If the device already exists, it is updated; otherwise, a new device is inserted.

    Returns:
        Response: A JSON object with a message and the appropriate HTTP status code:

        - 201: Device successfully inserted.
        - 200: Device successfully updated.
        - 400: Validation error in the request body.
        - 500: Internal server error while inserting into the database.
    """
	try:
	
		data = request.get_json()
		validated = DeviceSchema(**data)

		success, status = insert_device(validated.model_dump())
		if success:
			message = "Device inserted" if status == 201 else "Device updated"
			return jsonify({"message": message}), status
		else:
			return jsonify({"message": "Error inserting device into the database"}), 500
	
	except ValidationError as e:
		return jsonify({
			"message": "Required fields were not provided",
			"details": e.errors()
		}), 400
	
	except Exception as e:
		print("Error inserting document into MongoDB:", e)
		return jsonify({"message": "Error inserting document into MongoDB"}), 500
