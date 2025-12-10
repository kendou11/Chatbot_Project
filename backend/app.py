#backend/app.py
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db
from user import user_bp

app = Flask(__name__)
CORS(app)

# DB 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 블루프린트 등록
app.register_blueprint(user_bp, url_prefix="/api")




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)