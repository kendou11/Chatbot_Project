import certifi
import httpx
import os
import json
from flask import Blueprint, render_template, request, jsonify, session, current_app
from openai import OpenAI
from dotenv import load_dotenv
from backend.models import db, ChatLog, UseBox  # UseBox 모델 임포트 추가
from datetime import datetime, timezone

load_dotenv()

# 블루프린트 생성
bp = Blueprint('legal_chat', __name__, url_prefix='/legal')

# --- 챗봇 환경 설정 ---
USER_NAME = "자유로움"
CHAT_TITLE = "법률 및 생활 규제 정보 챗봇"

# 시스템 페르소나 설정 (기존 내용 100% 유지)
SYSTEM_PROMPT = """
당신은 일상생활에서 마주할 수 있는 법적 문제(계약, 분쟁, 소비)나 새로운 법규 해석, 부동산/주택 관련 법률, 노동법 등 쉽고 정확한 법률 및 규제 정보를 제공하는 '명쾌하고 신뢰할 수 있는 법률 어드바이저' 챗봇입니다.
사용자 이름: {user_name}

[범위 제한 및 거절 지침 - 최우선 순위]

당신의 답변 권한은 오직 '일반 법률 정보, 규제 및 행정 절차' 관련 정보에만 엄격히 국한됩니다.

위 전문 분야와 직접적인 관련이 없는 모든 주제(건강 상식, 음식, 날씨, 기술, 금융 투자 등)에 대해서는 단 한 문장의 정보도 제공하지 마십시오.

질문의 내용이 법률/규제가 아니라고 판단되면, 질문의 경중에 상관없이 즉시 아래 **[거절 템플릿]**만을 출력하십시오.

[거절 템플릿] "죄송합니다, {user_name}님. 저는 법률 및 생활 규제 정보 챗봇으로서 [사용자가 요청한 주제]와 같은 전문 영역이나 법률 외 분야에 대해서는 도움을 드릴 수 없습니다. 저는 오직 법률 정보와 절차 안내만 가능합니다. 다른 법률 관련 질문이 있으시다면 기꺼이 조언해 드리겠습니다."

[페르소나 & 역할]
1. 성격: 복잡한 법률 및 규제 내용을 쉽고 정확하게 해석하여 사용자에게 명료한 해답을 제시하는 전문가입니다.
2. 어조: 객관적이고 사실에 기반한 정보 전달과 함께, 상황 판단에 필요한 중요한 정보를 강조하는 간결한 대화체를 사용합니다.
3. 주요 역할: 사용자의 법률 관련 질문을 듣고, 관련 법규 및 절차에 대한 핵심 정보를 제공하며, 일상생활 법률 문제 해결을 위한 실질적인 가이드를 제공합니다.
4. 답변 Role: 답변은 반드시 [공감 & 문제 파악] → [관련 법규/원칙 요약] → [실질적 해결 방안] → [법률 전문가 제안] 순서로 구성되어야 합니다.

[답변 가이드라인]
1. 출력 형식: 답변 내용은 마크다운 형식(헤딩, 볼드, 목록)을 사용하여 가독성 높게 작성하며, 단계별 해결 방안은 명확한 목록으로 제시합니다.

[면책 조항]
7. 면책 조항: 답변의 마지막에 "⭐ 중요: 이 챗봇은 법률 정보를 제공하지만, 공식적인 법적 자문이나 소송 대리를 대체할 수 없습니다. 중요한 법적 문제에 대해서는 반드시 변호사 등 전문 법조인과 상담하시길 권장합니다."라는 면책 조항을 포함합니다.
"""

# OpenAI 클라이언트 초기화
client = None
try:
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(
            api_key=api_key,
            http_client=httpx.Client(verify=certifi.where())
        )
except Exception as e:
    print(f"[Legal] OpenAI Init Error: {e}")


# --- 1. 초기 안내 데이터 제공 (/legal/) ---
@bp.route('/')
def chat_usage():
    user_name = session.get('user_name', USER_NAME)
    user_id = session.get('user_id')

    chat_intro_html = f"""
    <div class="initial-text" style="margin-top: 5px;">
        <b>환영합니다!</b> {user_name}님!</b> {user_name}님의 복잡한 법률 문제를 명쾌하게 풀어드리는 '법률 및 생활 규제 정보' 챗봇입니다!
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        부동산 계약, 전세 계약 문제, 근로 계약 관련 법률, 새로운 정책이나 규제에 대한 궁금증까지! 어려운 법률 용어도 쉽고 명확하게 설명해 드릴 준비가 되어 있습니다. {user_name}님의 법률 고민을 지금 바로 저와 나눠보세요
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <b>어떤 질문을 해야 할까요?</b>
        <ul>
            <li>"아파트 층간소음 문제로 고통받고 있는데, 법적으로 어떻게 대응할 수 있을까요?"</li>
            <li>"쇼핑몰에서 불량품을 샀는데 환불이 어렵다고 해요. 소비자의 권리는 무엇인가요?"</li>
            <li>"근로계약서 작성 시 반드시 확인해야 할 사항이 궁금해요."</li>
            <li>"내용증명이 무엇이고 언제 사용해야 하나요?"</li>
        </ul>
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <span style="color: red; font-weight: bold;">꼭 기억해주세요!</span>
        <p>이 챗봇은 법률 정보를 제공하지만, 공식적인 법적 자문이나 법률 서비스, 소송 대리를 대체할 수 없습니다. <br>중요한 법적 문제에 대해서는 반드시 변호사 등 전문 법조인과 상담하시길 권장합니다.</p>
    </div><p>자, 이제 {user_name}님의 법률 관련 궁금증을 들려주세요. 제가 절차와 정보를 친절히 안내해 드릴게요!</p>
    """

    return jsonify({
        "status": "success",
        "user_name": user_name,
        "is_logged_in": bool(user_id),
        "chat_title": f"{user_name}님의 법률 자문",
        "intro_html": chat_intro_html
    })


# --- 2. API 호출 및 하이브리드 저장 (/legal/ask) ---
@bp.route('/ask', methods=['POST'])
def ask():
    if client is None:
        return jsonify({'response': 'Error: OpenAI API Key missing.'}), 500

    current_user_id = session.get('user_id', 1)
    print(f"[Legal/Ask] Processing for User ID: {current_user_id}")

    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_name = session.get('user_name', USER_NAME)

        if not user_message:
            return jsonify({'response': '메시지를 입력해주세요.'}), 400

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(user_name=user_name)},
            {"role": "user", "content": user_message}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1
        )

        ai_response = response.choices[0].message.content.strip()

        # --- 하이브리드 저장 로직 수정 (SQL + MongoDB + Vector DB) ---
        try:
            # 1. UseBox 권한 확인 및 생성 (법률 자문 ai_id = 7)
            LEGAL_AI_ID = 7
            usebox = UseBox.query.filter_by(user_id=current_user_id, ai_id=LEGAL_AI_ID).first()

            if not usebox:
                usebox = UseBox(user_id=current_user_id, ai_id=LEGAL_AI_ID)
                db.session.add(usebox)
                db.session.commit()

            # 2. SQL 저장 (usebox_id 필드 사용)
            new_log = ChatLog(
                usebox_id=usebox.use_id,
                question=user_message,
                answer=ai_response,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(new_log)
            db.session.commit()
            sql_id = new_log.id

            # 3. MongoDB 저장 (Atlas)
            mongodb = getattr(current_app, 'mongodb', None)
            if mongodb is not None:
                try:
                    mongodb.chat_history.insert_one({
                        "sql_id": sql_id,
                        "usebox_id": usebox.use_id,
                        "user_id": current_user_id,
                        "category": "legal",
                        "question": user_message,
                        "answer": ai_response,
                        "timestamp": datetime.now(timezone.utc)
                    })
                    print(">>> [SUCCESS] Legal data saved to MongoDB Atlas!")
                except Exception as mongo_err:
                    print(f"[Legal Mongo Error] {mongo_err}")

            # 4. Vector DB 저장
            vector_db = getattr(current_app, 'vector_db', None)
            if vector_db is not None:
                try:
                    vector_db.add(
                        documents=[user_message],
                        ids=[f"legal_{sql_id}"],
                        metadatas=[{"user_id": current_user_id, "category": "legal"}]
                    )
                except Exception as vec_err:
                    print(f"[Legal Vector Error] {vec_err}")

            print(f"[Legal] Hybrid Storage Success: User {current_user_id}")

        except Exception as db_err:
            db.session.rollback()
            print(f"[Legal Storage Error] {db_err}")

        return jsonify({'status': 'success', 'response': ai_response})

    except Exception as e:
        print(f"[Legal API Error] {e}")
        return jsonify({'response': '서버 통신 오류가 발생했습니다.'}), 500


# --- 3. 리포트 생성 함수 (/legal/report) ---
@bp.route('/report', methods=['GET'])
def generate_report():
    user_id = session.get('user_id', 1)

    try:
        # UseBox 조인을 통해 법률(ai_id=7) 기록만 필터링
        history = ChatLog.query.join(UseBox).filter(
            UseBox.user_id == user_id,
            UseBox.ai_id == 7
        ).order_by(ChatLog.created_at.desc()).limit(5).all()

        if not history:
            return jsonify({'error': '상담 내역이 부족합니다.'}), 404

        chat_data = "\n".join([f"Q: {h.question}\nA: {h.answer}" for h in reversed(history)])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 법률 전문가입니다. 상담 내역을 분석하여 요약 보고서를 작성하세요."},
                {"role": "user", "content": f"상담 내역 분석 보고서 작성:\n\n{chat_data}"}
            ]
        )

        return jsonify({'status': 'success', 'report': response.choices[0].message.content})

    except Exception as e:
        print(f"[Legal Report Error] {e}")
        return jsonify({'error': '리포트 생성 중 오류가 발생했습니다.'}), 500