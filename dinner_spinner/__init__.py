"""Dinner Spinner V1 — Flask application factory."""

from flask import Flask
from sqlalchemy import event
from sqlalchemy.engine import Engine


@event.listens_for(Engine, "connect")
def _enable_sqlite_fk(dbapi_connection, connection_record):
    """Enable SQLite foreign key enforcement for every connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Default configuration
    import os
    db_path = os.path.join(os.path.dirname(__file__), '..', 'dinner_spinner.db')
    app.config.update(
        SECRET_KEY="dev-secret-change-in-production",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Override with provided config
    if config:
        app.config.update(config)

    # Initialize extensions
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)

    # Import Base from models (avoids circular import)
    from dinner_persistence.models import Base
    db.Model = Base

    # Initialize the unit system
    from dinner_spinner.domain.unit_system import initialize
    initialize()

    # Register blueprints
    from dinner_spinner.presentation.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app


# Don't create app at module level - let the entry point do it
# This prevents import-time side effects during testing

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)