from flask import Flask, send_from_directory, jsonify
from app.routes.telemetry_route import telemetry_bp
from app.routes.device_route import device_bp
from app.mqtt_client import start_mqtt
from flask_cors import CORS
import os

def create_app(testing=False):
    """
    Creates and configures the Flask application instance.

    Registers blueprints, enables CORS, and sets up Swagger routes.

    Args:
        testing (bool, optional): Indicates whether the app is running in a testing environment. Defaults to False.

    Returns:
        Flask: A configured Flask application instance.
    """
    app = Flask(__name__)
    app.register_blueprint(telemetry_bp)
    app.register_blueprint(device_bp)
    CORS(app)

    @app.route('/swagger.yaml')
    def swagger_yaml():
        """
        Serves the Swagger YAML file used for API documentation.

        Returns:
            Response: The contents of the `swagger.yaml` file with appropriate content type.
        """
        with open("app/swagger.yaml", "r") as f:
            return f.read(), 200, {'Content-Type': 'application/yaml'}

    @app.route('/docs')
    def swagger_ui():
        """
        Serves the Swagger UI static HTML page for visualizing API documentation.

        Returns:
            Response: The Swagger UI HTML page.
        """
        return send_from_directory('static/swagger-ui', 'index.html')

    return app

if __name__ == '__main__':
    # Only starts the MQTT client in the main process (not during Flask reloader).
    print('WERKZEUG_RUN_MAIN:', os.environ.get('WERKZEUG_RUN_MAIN'))
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or os.environ.get('WERKZEUG_RUN_MAIN') is None:
        start_mqtt()

    create_app().run(host='0.0.0.0', debug=False, use_reloader=False, port=3000)