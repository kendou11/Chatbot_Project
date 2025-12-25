# backend/app.py
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# --- [DB 관련 라이브러리 추가] ---
from pymongo import MongoClient
import chromadb
from chromadb.utils import embedding_functions  # 임베딩 함수 추가

# --- [ 기본 Blueprint import] ---
from backend.models import db
from backend.views.user import user_bp
from backend.views.notice import notice_bp
from backend.views.review import review_bp
from backend.views.main import main_bp
from backend.views.mypage import mypage_bp

# --- [ 챗봇 Blueprint import] ---
from backend.views.Chatbot.wellness_views import bp as wellness_bp
from backend.views.Chatbot.career_views import bp as career_bp
from backend.views.Chatbot.daily_views import bp as daily_bp
from backend.views.Chatbot.finance_views import bp as finance_bp
from backend.views.Chatbot.health_views import bp as health_bp
from backend.views.Chatbot.learning_views import bp as learning_bp
from backend.views.Chatbot.legal_views import bp as legal_bp
from backend.views.Chatbot.tech_views import bp as tech_bp
from backend.views.Chatbot.history_views import bp as history_bp

def create_app():
    load_dotenv() #.env파일 세팅
    app = Flask(__name__)

    # CORS 설정: React(3000)와 통신 허용
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
    #CORS(app)

    # 1. SQLAlchemy(SQLite) 설정
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///AI.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "your-secret-key")

    # 2. MongoDB 초기화 (is not None 체크를 위해 안전하게 연결)
    try:
        mongo_client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        # chatbot_master DB 연결
        app.mongodb = mongo_client["chatbot_master"]
        # 연결 확인
        mongo_client.server_info()
        print("[SUCCESS] MongoDB Connected: 'chatbot_master'")
    except Exception as e:
        print(f"[ERROR] MongoDB Connection Failed: {e}")
        app.mongodb = None

    # 3. Vector DB(ChromaDB) 초기화 (Embedding Function 필수 설정)
    try:
        persist_dir = os.path.join(os.getcwd(), "chroma_db")
        chroma_client = chromadb.PersistentClient(path=persist_dir)

        # 텍스트를 벡터로 자동 변환해주는 기본 임베딩 함수 설정
        # (이 설정을 해야 .add() 호출 시 텍스트만 넣어도 저장이 됩니다)
        default_ef = embedding_functions.DefaultEmbeddingFunction()

        # 컬렉션 생성 및 할당
        app.vector_db = chroma_client.get_or_create_collection(
            name="chatbot_history",
            embedding_function=default_ef
        )
        print("[SUCCESS] Vector DB Initialized with Embedding Function")
    except Exception as e:
        print(f"[ERROR] Vector DB Initialization Failed: {e}")
        app.vector_db = None

    # DB 초기화
    db.init_app(app)
    Migrate(app, db)

    # --- [블루프린트 등록] ---
    # 1. 기존 프로젝트 기능
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(notice_bp, url_prefix="/api")
    app.register_blueprint(review_bp, url_prefix="/api")
    app.register_blueprint(main_bp, url_prefix="/api")
    app.register_blueprint(mypage_bp, url_prefix="/api")

    # 2. 8개 챗봇 기능 (각 파일에서 설정된 url_prefix가 적용됨)
    app.register_blueprint(wellness_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(daily_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(learning_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(tech_bp)
    app.register_blueprint(history_bp)

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # SQLite 테이블 생성
        db.create_all()

    # host="0.0.0.0"으로 설정하여 외부 접속 허용, debug=True로 자동 재시작 활성화
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt:
        print("Server stopped by user.")