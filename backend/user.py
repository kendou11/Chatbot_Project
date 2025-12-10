from flask import Blueprint, jsonify, request
from models import db, User

user_bp = Blueprint('api', __name__, url_prefix='/api')

@user_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

#Axios POST (DB에 데이터 추가)
@user_bp.route("/users", methods=["POST"])
def add_user():
    data = request.json
    user = User(name=data['name'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

# 라우트 이용 방법에 대해 연습용 글자 출력
@user_bp.route('/test')
def test():
    return jsonify({"msg": "Flask OK"})

# 라우트 이용 방법에 대해 연습용 api데이터제공 및 출력
@user_bp.route("/sample", methods=["GET"])
def sample():
    data = [{"name": "백기림", "value": 123},{"name": "이상수", "value": 3344}]
    return jsonify(data)