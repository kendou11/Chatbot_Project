from flask import Blueprint, request, jsonify
from backend.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.exc import IntegrityError

user_bp = Blueprint('api', __name__, url_prefix='/api')

@user_bp.route("/users/check/<type>", methods=["GET"])
def check_user(type):
    """실시간 중복 체크 API"""
    value = request.args.get('value')
    if not value:
        return jsonify({'available': False, 'message': '값이 비어있습니다.'}), 400

    if type == 'email':
        exists = User.query.filter_by(user_email=value).first()
    elif type == 'nickname':
        exists = User.query.filter_by(user_nickname=value).first()
    else:
        return jsonify({'available': False, 'message': '잘못된 타입입니다.'}), 400

    return jsonify({
        'available': exists is None,
        'message': '사용 가능합니다' if exists is None else '이미 사용중입니다.'
    })

'''
유저 중복 체크 api 명세서

호출 api 주소 : /users/check/<type>
리턴 값 : {available: 가능여부 , message: 에러메세지}

여러 상황 제시 
값이 비었을 경우 False , 값이 비었습니다
타입이 email 과 nickname 인 상태에서 
    중복이 없을 경우 각 available 에 값 넣고 , 사용 가능합니다 
    중복이 있을 경우 값넣고,  이미 사용중입니다
그 외 타입은  False, 잘못된 타입입니다. 제공 
'''



@user_bp.route("/users", methods=["POST"])
def add_user():
    """회원가입 API"""
    data = request.json

    # 필수 필드 검증
    check_user = ['nickname', 'email']
    for i in check_user:
        if not data.get(i):
            return jsonify({'error': f'{i}는 필수입니다.'}), 400


    # 중복 체크 이미 한번 확인하지만 또 확인하기
    if User.query.filter_by(user_email=data['email']).first():
        return jsonify({'error': '이메일이 이미 사용중입니다.'}), 409
    if User.query.filter_by(user_nickname=data['nickname']).first():
        return jsonify({'error': '닉네임이 이미 사용중입니다.'}), 409

    try:
        # 비밀번호 해시 처리 (소셜로그인 아닌 경우만)
        password = data.get('password', '')
        hashed_password = generate_password_hash(password) if password else None

        # User 생성 (모델 필드에 정확히 맞춤)
        user = User(
            user_email=data['email'],
            user_password=hashed_password,
            user_nickname=data['nickname'],
            user_image=data.get('image', '기본이미지'),  # 프론트에서 안보내면 기본값
            user_birthdate=datetime.strptime(data.get('birthdate', ''), '%Y-%m-%d').date()
            if data.get('birthdate') and len(data.get('birthdate', '')) == 10 else None,
            user_is_social=False,  # 기본 로컬 로그인
            user_money=0  # 기본값
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 201

    #상황에 따른 에러메세지 출력 부분
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': '데이터베이스 오류가 발생했습니다.'}), 500
    except ValueError:
        db.session.rollback()
        return jsonify({'error': '생년월일 형식이 올바르지 않습니다.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '회원가입 중 오류가 발생했습니다.'}), 500

'''
회원가입 api 명세서 post 타입

호출 api 주소 : /users
리턴 값 : {성공 여부, 메세지}

여러 상황 제시 
1. 데이터 받아오기
2. 아이디 이메일 존재 여부 확인후 없으면 error
3. 아이디 이메일 중복체크 한번더 확인후 중복시 error
4. 문제 없으면 비밀번호 암호화시키기
5. user 생성 및 add commmit 
6. 마무리 되면 리턴 success 
7. 3가지 에러 상황에 대해서 각 오류에 대한 에러메세지 error
'''


@user_bp.route("/users/login", methods=["POST"])
def user_login():
    """로그인 검증 API """
    data= request.get_json()
    email = data.get('email')
    password = data.get('password')

    # 사용자와 비밀번호 전달 받지 못했을 때
    if not email or not password:
        return jsonify({'success': False, 'message': '이메일과 비밀번호를 입력하세요.'}), 400

    user_data = User.query.filter_by(user_email=email).first()

    # 사용자 없거나 비밀번호 불일치할 때
    if not user_data or not check_password_hash(user_data.user_password, password):
        return jsonify({'success': False, 'message': '이메일 또는 비밀번호가 틀립니다.'}), 401

    # 로그인 성공 시 닉네임, 이메일 반환
    return jsonify({
        'success': True,
        'message': '로그인 성공',
        "nickname": user_data.user_nickname,
    })
