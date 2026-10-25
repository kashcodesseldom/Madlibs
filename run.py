from app import create_app
from scripts.seed_db import seed_if_empty

app = create_app()

with app.app_context():
    seed_if_empty()  # first run: load the starter stories

if __name__ == "__main__":
    app.run(debug=True)
