# api/main.py
from flask import Blueprint, jsonify, request
from backend.models import Notice, BasicAI, User, CustomAI, UseBox, db

main_bp = Blueprint("main", __name__)


@main_bp.route("/main/summary", methods=["GET"])
def get_main_summary():
    """메인 화면: 공통 데이터 + 로그인시 개인화 데이터"""

    # 1. 공통 데이터: Notice (모든 활성 게시글)
    notices = db.session.query(
        Notice.notice_id,
        Notice.user_id,
        Notice.notice_title,
        Notice.notice_view_count,
        User.user_nickname
    ).outerjoin(
        User, Notice.user_id == User.user_id
    ).filter(
        Notice.notice_delete == False
    ).order_by(
        Notice.notice_new.desc()
    ).all()

    notice_list = [
        {
            "notice_id": n.notice_id,
            "user_id": n.user_id,
            "notice_title": n.notice_title,
            "notice_view_count": n.notice_view_count,
            "user_nickname": n.user_nickname
        }
        for n in notices
    ]

    # 2. 공통 데이터: BasicAI (모든 기본 AI)
    AIs = BasicAI.query.filter(
        BasicAI.ai_type == False
    ).order_by(
        BasicAI.ai_id.desc()
    ).all()

    ai_list = [
        {
            "ai_id": ai.ai_id,
            "ai_name": ai.ai_name,
            "ai_tip": ai.ai_tip,
            "ai_image": ai.ai_image,
            "ai_content":ai.ai_content

        }
        for ai in AIs
    ]

    response = {
        "success": True,
        "notice": notice_list,
        "basic_ai": ai_list,
    }

    # 3. 로그인 사용자 확인 (토큰 있으면)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        nickname = auth_header.replace("Bearer ", "")
        user = User.query.filter_by(
            user_nickname=nickname,
            user_delete=False
        ).first()

        if user:
            # 개인화 데이터 추가
            response["user"] = {
                "user_nickname": user.user_nickname,
            }

            # 나의 커스텀 AI (판매중)
            custom_ais = db.session.query(
                CustomAI, BasicAI
            ).join(BasicAI, CustomAI.ai_id == BasicAI.ai_id).filter(
                CustomAI.user_id == user.user_id,
                CustomAI.custom_delete == False,
            ).all()

            response["custom_ai"] = [
                {
                    "ai_name": b.ai_name,
                    "ai_tip": b.ai_tip,
                    "ai_image": b.ai_image,
                }
                for c, b in custom_ais
            ]
    return jsonify(response)
