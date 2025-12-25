from flask import Blueprint, render_template, session, jsonify
from backend.models import db, ChatLog
from backend.views.database import get_mongo_db

bp = Blueprint('history', __name__, url_prefix='/history')


@bp.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return "로그인이 필요한 서비스입니다.", 401

    # 1. SQL에서 해당 유저의 최근 대화 목록 20개 가져오기
    logs = ChatLog.query.filter_by(user_id=user_id).order_by(ChatLog.created_at.desc()).limit(20).all()
    return render_template('history/index.html', logs=logs)


@bp.route('/detail/<int:sql_id>')
def detail(sql_id):
    # 2. 특정 대화 클릭 시 MongoDB에서 전문 가져오기
    mongodb = get_mongo_db()
    chat_detail = mongodb.chat_history.find_one({"sql_id": sql_id})

    if chat_detail:
        # MongoDB의 ObjectId는 JSON 변환이 안 되므로 문자열로 변환
        chat_detail['_id'] = str(chat_detail['_id'])
        return jsonify(chat_detail)
    return jsonify({"error": "기록을 찾을 수 없습니다."}), 404