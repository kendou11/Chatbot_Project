from flask import request, jsonify, Blueprint
from functools import wraps
from werkzeug.security import generate_password_hash

from backend.models import db, User
from urllib.parse import unquote
from datetime import datetime

mypage_bp = Blueprint("mypage", __name__)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({'success': False, 'message': '로그인 필요합니다.'}), 401

        raw_token = auth_header.replace("Bearer ", "")
        nickname_token = unquote(raw_token)

        user = User.query.filter_by(user_nickname=nickname_token).first()
        if not user:
            return jsonify({'success': False, 'message': '유저를 찾을 수 없습니다.'}), 404

        return f(user=user, *args, **kwargs)  # user 객체를 함수에 전달

    return decorated_function


@mypage_bp.route("/users/mypage", methods=["PATCH"])
@token_required
def update_user_profile(user):
    """로그인한 사용자 프로필 수정 API"""
    data = request.json

    updated = False

    # 닉네임 수정 (중복 체크 포함)
    if 'nickname' in data and data['nickname'] != user.user_nickname:
        if User.query.filter_by(user_nickname=data['nickname']).first():
            return jsonify({'success': False, 'message': '닉네임이 이미 사용중입니다.'}), 409
        user.user_nickname = data['nickname']
        updated = True

    # 비밀번호 수정 (user_password) - 옵션
    if 'password' in data and data['password']:
        user.user_password = generate_password_hash(data['password'])
        updated = True

    # 이미지 수정
    if 'image' in data:
        user.user_image = data['image']
        updated = True

    # 업로드 없을 떄
    if not updated:
        return jsonify({'success': False, 'message': '수정할 필드가 없습니다.'}), 400

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '프로필이 업데이트되었습니다.',
            'user': user.to_dict()
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': '업데이트 중 오류가 발생했습니다.'}), 500

@mypage_bp.route("/users/mypage", methods=["GET"])
@token_required
def get_user_profile(user):
    return jsonify({
        "success": True,
        "user_nickname": user.user_nickname,
        "user_money": user.user_money,                 
        "image": user.user_image,
                }), 200