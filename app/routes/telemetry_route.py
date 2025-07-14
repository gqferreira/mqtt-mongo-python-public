from flask import Blueprint, request, jsonify
from app.services.telemetry_service import list_telemetry

telemetry_bp = Blueprint('telemetry', __name__, url_prefix='/telemetry')

@telemetry_bp.route('', methods=['GET'])
def get_all_telemetries():
	"""
    Retrieves all telemetry records from the database.

    Returns:
        Response: A JSON list of all telemetry entries and the appropriate HTTP status code.

        - 200: Telemetries successfully retrieved.
        - 500: Internal server error while accessing the database.
	"""
	response, status = list_telemetry()
	return jsonify(response), status

@telemetry_bp.route('/<string:channel>', methods=['GET'])
def get_channel_telemetries(channel):
	"""
    Retrieves telemetry records filtered by channel.

    Args:
        channel (str): The name or identifier of the telemetry channel.

    Returns:
        Response: A JSON list of telemetry entries for the specified channel and the appropriate HTTP status code.

        - 200: Channel telemetries successfully retrieved.
        - 404: No telemetry found for the given channel.
        - 500: Internal server error while accessing the database.
	"""
	response, status = list_telemetry(channel)
	return jsonify(response), status
