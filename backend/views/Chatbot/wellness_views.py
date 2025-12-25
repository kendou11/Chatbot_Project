import certifi
import httpx
import os
import json
from flask import Blueprint, render_template, request, session, jsonify, current_app
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timezone
from backend.models import db, ChatLog

# 환경 변수 로드
load_dotenv()

# 블루프린트 설정
bp = Blueprint('wellness_chat', __name__, url_prefix='/wellness')

# --- 챗봇 환경 설정 ---
USER_NAME = "사용자님"
CHAT_TITLE = "정신 · 건강 웰니스 코치"

# 시스템 프롬프트
SYSTEM_PROMPT = """
당신은 사용자의 심리적 안정, 스트레스 관리, 명상, 숙면, 그리고 긍정적인 마음가짐을 돕는 '정신 건강 및 웰니스 코치'입니다.
사용자 이름: {user_name}

[필수 지침]
1. 답변은 항상 따뜻하고 공감하며, 사용자가 정서적 지지를 받고 있다는 느낌을 주어야 합니다.
2. 질문이 웰니스 범위를 벗어날 경우(예: 주식 투자, 코딩, 법률 등), 거절 템플릿을 사용하여 정중히 답변을 거절하세요.
3. 답변은 마크다운(Markdown) 형식을 사용하여 가독성 있게 작성합니다.
4. 역할 및 범위 제한: 당신은 의학적 진단이나 약물 처방을 할 수 없습니다. 답변 끝에 반드시 면책 조항을 포함하세요.

[거절 템플릿]
"저는 정신 건강 및 웰니스 코치로서 [요청한 주제]와 같은 전문 분야에 대해서는 도움을 드릴 수 없습니다. 마음 돌봄이나 스트레스 관리와 같은 웰빙 주제로 질문해 주시면 성심껏 도와드리겠습니다."
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
    print(f"[Wellness] OpenAI Init Error: {e}")


# --- 1. 초기 안내 데이터 제공 (/wellness/) ---
@bp.route('/')
def chat_usage():
    user_name = session.get('user_name', USER_NAME)
    user_id = session.get('user_id')

    intro_html = f"""
    <div class="initial-text" style="margin-top: 5px;">
        <b>환영합니다!</b> {user_name}님의 마음의 평화와 웰빙을 위한 '정신 · 건강 웰니스' 챗봇입니다!
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        일상 속 스트레스, 불안, 슬픔부터 숙면, 명상, 긍정적인 마음가짐까지! 이곳에서 당신의 마음을 돌보고 건강하게 유지하기 위한 다양한 정보와 대화를 나눌 수 있습니다.
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <b>어떤 질문을 해야 할까요?</b>
        <ul>
            <li>"요즘 스트레스가 너무 많아서 잠을 못 자요. 어떻게 하면 좋을까요?"</li>
            <li>"마음을 진정시키는 명상 방법이 있나요?"</li>
            <li>"불안한 마음을 다스리는 긍정적인 확언을 알려주세요."</li>
        </ul>
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <span style="color: red; font-weight: bold;">⭐꼭 기억해주세요!</span>
        <p>이 챗봇은 당신의 정신 건강과 웰빙을 위한 정보와 지원을 제공하지만, 전문적인 진단이나 의학적인 치료를 대체할 수는 없습니다.</p>
    </div>
    <p>자, 이제 {user_name}님의 마음 이야기를 들려주세요. 제가 {user_name}님의 여정을 함께할게요!</p>
    """
    return jsonify({
        "status": "success",
        "user_name": user_name,
        "is_logged_in": bool(user_id),
        "chat_title": CHAT_TITLE,
        "intro_html": intro_html
    })


# --- 2. API 호출 및 하이브리드 저장 (/wellness/ask) ---
@bp.route('/ask', methods=['POST'])
def ask():
    if client is None:
        return jsonify({'response': '서버의 AI 서비스 설정이 완료되지 않았습니다.'}), 500

    current_user_id = session.get('user_id', 1)
    print(f"[Wellness/Ask] Processing for User ID: {current_user_id}")

    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_name = session.get('user_name', USER_NAME)

        if not user_message:
            return jsonify({'response': '메시지를 입력해주세요.'}), 400

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(user_name=user_name)},
                {"role": "user", "content": user_message}
            ],
            max_tokens=2048,
            temperature=0.7
        )
        gpt_response = response.choices[0].message.content.strip()

        disclaimer = "\n\n⭐ **중요**: 이 답변은 정보 제공용이며 전문적인 의료 진단을 대체할 수 없습니다."
        if "의학적인 치료를 대체" not in gpt_response:
            gpt_response += disclaimer

        # --- 하이브리드 저장 로직 ---
        try:
            # 1. SQL 저장
            new_log = ChatLog(
                user_id=current_user_id,
                category='wellness',
                question=user_message,
                answer=gpt_response,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(new_log)
            db.session.commit()
            sql_id = new_log.id

            # 2. MongoDB 저장 (is not None 필수)
            mongodb = getattr(current_app, 'mongodb', None)
            if mongodb is not None:
                try:
                    mongodb.chat_history.insert_one({
                        "sql_id": sql_id,
                        "user_id": current_user_id,
                        "category": "wellness",
                        "question": user_message,
                        "answer": gpt_response,
                        "timestamp": datetime.now(timezone.utc)
                    })
                except Exception as mongo_err:
                    print(f"[Wellness Mongo Error] {mongo_err}")

            # 3. Vector DB 저장 (is not None 필수)
            vector_db = getattr(current_app, 'vector_db', None)
            if vector_db is not None:
                try:
                    vector_db.add(
                        documents=[user_message],
                        ids=[f"wellness_{sql_id}"],
                        metadatas=[{"user_id": current_user_id, "category": "wellness"}]
                    )
                except Exception as vec_err:
                    print(f"[Wellness Vector Error] {vec_err}")

            print(f"[Wellness] Hybrid Storage Success: User {current_user_id}")

        except Exception as db_err:
            db.session.rollback()
            print(f"[Wellness Storage Error] {db_err}")

        return jsonify({'status': 'success', 'response': gpt_response})

    except Exception as e:
        print(f"[Wellness API Error] {e}")
        return jsonify({'response': '대화 중 오류가 발생했습니다.'}), 500


# --- 3. 리포트 생성 함수 (/wellness/report) ---
@bp.route('/report', methods=['GET', 'POST'])
def generate_report():
    user_id = session.get('user_id', 1)

    try:
        logs = ChatLog.query.filter_by(user_id=user_id, category='wellness') \
            .order_by(ChatLog.created_at.desc()).limit(10).all()

        if not logs:
            return jsonify({'report': '마음 분석을 위한 대화 내역이 아직 부족합니다. 저와 좀 더 대화해 볼까요?'}), 404

        chat_history = "\n".join([f"Q: {log.question}\nA: {log.answer}" for log in reversed(logs)])

        analysis_prompt = f"""
        당신은 전문 심리 상담가이자 웰니스 분석가입니다. 
        다음 대화 내역을 바탕으로 사용자의 현재 심리적 상태, 주요 스트레스 요인, 
        그리고 마음의 평화를 찾기 위한 맞춤형 웰니스 처방전(명상, 행동 요령 등)을 작성해 주세요.
        답변은 마크다운 형식으로 따뜻하고 정중하게 작성해 주세요.

        [대화 내역]
        {chat_history}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "마음을 치유하는 전문 분석가 역할을 수행합니다."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.7
        )

        return jsonify({'status': 'success', 'report': response.choices[0].message.content.strip()})

    except Exception as e:
        print(f"[Wellness Report Error] {e}")
        return jsonify({'error': '분석 보고서 생성 중 오류가 발생했습니다.'}), 500