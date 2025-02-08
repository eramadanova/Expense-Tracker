"""
Main entry point of the application.

This module initializes and runs the Flask application.
It creates the application context and sets up the database.
"""

from src import create_app, db

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
