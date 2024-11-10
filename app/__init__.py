from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Register Blueprints here if needed
    from .routes import dashboard
    app.register_blueprint(dashboard)

    return app