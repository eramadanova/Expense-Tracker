from app import create_app, db
from app.models import Category

app = create_app()

# Създаване на базата данни
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
