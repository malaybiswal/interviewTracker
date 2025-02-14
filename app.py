from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from models import db
from routes import routes

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
CORS(app)  # Enable CORS for frontend

app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True)
