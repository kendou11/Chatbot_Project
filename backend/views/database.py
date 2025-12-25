import sqlite3
from pymongo import MongoClient
import os

# --- [1] SQL 설정 (기본 정보 관리) ---
def get_sql_conn():
    db_path = os.path.join(os.getcwd(), 'project.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# --- [2] MongoDB 설정 (긴 보고서 & 대화 전문 저장) ---
def get_mongo_db():
    try:
        # 타임아웃 설정을 추가하여 엔진이 없을 때 서버가 무한 대기하는 것을 방지합니다.
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        return client['chatbot_master']
    except Exception as e:
        print(f"⚠️ [System] MongoDB 연결 실패: {e}")
        return None

# --- [3] Vector DB 설정 (ChromaDB) ---
def get_vector_collection():
    try:
        import chromadb
        from chromadb.utils import embedding_functions

        # 'vector_storage' 폴더에 데이터를 영구 저장
        client = chromadb.PersistentClient(path="./vector_storage")

        # 임베딩 모델 설정
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="jhgan/ko-sroberta-multitask"
        )

        return client.get_or_create_collection(name="user_chats", embedding_function=ef)
    except Exception as e:
        # 패키지가 없거나 모델 로드 실패 시 None 반환
        print(f"⚠️ [System] Vector DB 연결 실패 (건너뜀): {e}")
        return None