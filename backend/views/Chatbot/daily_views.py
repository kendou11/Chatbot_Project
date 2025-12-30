import certifi
import httpx
import os
import json
from flask import Blueprint, render_template, request, jsonify, session, current_app
from openai import OpenAI
from dotenv import load_dotenv
from backend.models import db, ChatLog, UseBox
from datetime import datetime, timezone

load_dotenv()

# 블루프린트 생성
bp = Blueprint('daily_chat', __name__, url_prefix='/daily')

# --- 챗봇 환경 설정 ---
# [수정] 고정 닉네임 제거 및 기본값 설정
DEFAULT_NAME = "사용자"
CHAT_TITLE = "일상생활 문제 해결 챗봇"

# 시스템 페르소나 설정 (기존 내용 유지하되 닉네임 주입 가능하도록 설정)
SYSTEM_PROMPT = """
당신은 요리 레시피부터 가전제품 사용법, 육아 및 반려동물 돌봄 노하우, 주택 관리 팁, 특정 지역의 생활 정보까지, 일상에서 마주하는 다양한 문제들을 해결해 드리는 '친절하고 만능인 생활 도우미' 챗봇입니다.
사용자 이름: {user_name}

[범위 제한 및 거절 지침 - 최우선 순위]

당신의 답변 권한은 오직 **'일상적인 안부 및 가벼운 일반 대화'**에만 엄격히 국한됩니다.

위 전문 분야와 직접적인 관련이 없는 모든 전문 주제(의료 진단, 법률 자문, 금융 투자, 심리 상담 등)에 대해서는 단 한 문장의 정보도 제공하지 마십시오.

질문이 가벼운 일상이 아닌 전문적인 상담을 요구한다고 판단되면 즉시 아래 **[거절 템플릿]**만을 출력하십시오.

[거절 템플릿] "죄송합니다, {user_name}님. 저는 일상 대화 챗봇으로서 [사용자가 요청한 주제]와 같은 전문적인 진단이나 자문 분야에 대해서는 도움을 드릴 수 없습니다. 대신 가벼운 일상 이야기나 일반적인 정보에 대해 궁금한 점이 있으시다면 기꺼이 대화해 드리겠습니다."

[페르소나 & 역할]
1. 성격: 다양한 일상생활 질문에 대해 빠르고 정확하게 답해주며, 사용자의 편의를 최우선으로 생각하는 똑똑한 도우미입니다.
2. 어조: 쉽고 친근하게 정보를 전달하며, 문제 해결에 대한 실질적인 방법을 제시하는 실용적인 대화체를 사용합니다.
3. 주요 역할: 요리, 가전, 육아, 주거, 지역 정보 등 광범위한 생활 정보 제공 및 문제 해결 팁 안내를 통해 삶의 질을 높이도록 돕습니다.
4. 답변 Role: 답변은 반드시 [공감 & 문제 파악] → [핵심 원칙/노하우] → [단계별 해결 가이드] → [추가 팁 & 전문가 연계] 순서로 구성되어야 합니다.

[답변 가이드라인]
1. 출력 형식: 답변 내용은 마크다운 형식(헤딩, 볼드, 목록)을 사용하여 가독성 높게 작성하며, 단계별 해결 가이드는 명확한 목록으로 제시합니다.

[면책 조항]
7. 면책 조항: 답변의 마지막에 "⭐ 중요: 이 챗봇은 생활 정보를 제공하지만, 전문적인 진단이나 수리, 안전에 직결되는 기술적인 조언을 직접 대체할 수 없습니다. 중요한 문제에 대해서는 해당 분야의 전문가와 상담하시길 권장합니다."라는 면책 조항을 포함합니다.
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
    print(f"[Daily] OpenAI Init Error: {e}")


# --- 1. 초기 안내 데이터 제공 (/daily/) ---
@bp.route('/')
def chat_usage():
    # [수정] 실시간 닉네임 확보 (우선순위: user_nickname -> user_name -> 기본값)
    user_name = session.get('user_nickname') or session.get('nickname') or session.get('user_name') or session.get('name') or DEFAULT_NAME
    user_id = session.get('user_id')

    # [수정] intro_html 내의 닉네임 누락 및 고정 이름 수정
    chat_intro_html = f"""
    <div class="initial-text" style="margin-top: 5px;">
        <b>환영합니다!</b> {user_name}님! {user_name}님의 편리하고 스마트한 일상을 위한 '일상생활 문제 해결' 챗봇입니다
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        오늘 저녁 메뉴 고민, 새로 산 가전제품 사용법, 아이와 즐거운 시간을 보내는 방법, 반려동물 양육 팁, 집수리 노하우, 이웃 지역 정보까지! 삶의 질을 높이고 일상 속 불편함을 해소하기 위한 모든 질문에 제가 명쾌한 답변을 드릴 준비가 되어 있습니다.
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <b>어떤 질문을 해야 할까요?</b>
        <ul>
            <li>"냉장고에 남은 재료로 만들 수 있는 간단한 저녁 메뉴가 있을까요? (양파, 계란, 스팸이 있어요)"</li>
            <li>"새로 산 세탁기가 작동을 안 하는데, 고장인가요?"</li>
            <li>"우리 아이에게 좋은 영양 간식을 추천해 주세요."</li>
            <li>"곰팡이가 핀 화장실 타일을 깨끗하게 청소하는 방법이 궁금해요."</li>
        </ul>
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <span style="color: red; font-weight: bold;">꼭 기억해주세요!</span>
        <p>이 챗봇은 다양한 생활 정보를 제공하지만, 전문적인 진단이나 수리, 안전에 직결되는 기술적인 조언을 직접 대체할 수 없습니다. 중요한 문제에 대해서는 해당 분야의 전문가와 상담하시길 권장합니다.</p>
    </div>
    <p style="margin-top: 10px;">자, 이제 <b>{user_name}님</b>의 일상 이야기를 들려주세요. 제가 함께할게요!</p>
    """

    return jsonify({
        "status": "success",
        "user_name": user_name,
        "is_logged_in": bool(user_id),
        "chat_title": CHAT_TITLE,
        "intro_html": chat_intro_html
    })


# --- 2. API 호출 및 하이브리드 저장 (/daily/ask) ---
@bp.route('/ask', methods=['POST'])
def ask():
    if client is None:
        return jsonify({'response': 'Error: OpenAI API Key missing.'}), 500

    current_user_id = session.get('user_id', 1)
    # [수정] 질문 처리 시에도 실시간 닉네임 사용
    user_name = session.get('user_nickname') or session.get('user_name') or DEFAULT_NAME

    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'response': '메시지를 입력해주세요.'}), 400

        # [수정] 페르소나에 실제 닉네임 주입
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

        # --- 하이브리드 저장 로직 ---
        try:
            DAILY_AI_ID = 5  # 예시 ID 유지
            usebox = UseBox.query.filter_by(user_id=current_user_id, ai_id=DAILY_AI_ID).first()

            if not usebox:
                usebox = UseBox(user_id=current_user_id, ai_id=DAILY_AI_ID)
                db.session.add(usebox)
                db.session.commit()

            new_log = ChatLog(
                usebox_id=usebox.use_id,
                question=user_message,
                answer=ai_response,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(new_log)
            db.session.commit()
            sql_id = new_log.id

            mongodb = getattr(current_app, 'mongodb', None)
            if mongodb is not None:
                try:
                    mongodb.chat_history.insert_one({
                        "sql_id": sql_id,
                        "usebox_id": usebox.use_id,
                        "user_id": current_user_id,
                        "category": "daily",
                        "question": user_message,
                        "answer": ai_response,
                        "timestamp": datetime.now(timezone.utc)
                    })
                except Exception as mongo_err:
                    print(f"[Daily Mongo Error] {mongo_err}")

            vector_db = getattr(current_app, 'vector_db', None)
            if vector_db is not None:
                try:
                    vector_db.add(
                        documents=[user_message],
                        ids=[f"daily_{sql_id}"],
                        metadatas=[{"user_id": current_user_id, "category": "daily"}]
                    )
                except Exception as vec_err:
                    print(f"[Daily Vector Error] {vec_err}")

        except Exception as db_err:
            db.session.rollback()
            print(f"[Daily Storage Error] {db_err}")

        return jsonify({'status': 'success', 'response': ai_response})

    except Exception as e:
        print(f"[Daily API Error] {e}")
        return jsonify({'response': '서버 통신 오류가 발생했습니다.'}), 500


# --- 3. 리포트 생성 함수 (/daily/report) ---
@bp.route('/report', methods=['GET'])
def generate_report():
    user_id = session.get('user_id', 1)
    # [수정] 리포트용 사용자 이름 확보
    user_name = session.get('user_nickname') or session.get('user_name') or DEFAULT_NAME

    try:
        history = ChatLog.query.join(UseBox).filter(
            UseBox.user_id == user_id,
            UseBox.ai_id == 5
        ).order_by(ChatLog.created_at.desc()).limit(5).all()

        if not history:
            return jsonify({'error': '분석할 상담 내역이 부족합니다.'}), 404

        chat_data = "\n".join([f"Q: {h.question}\nA: {h.answer}" for h in reversed(history)])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": f"당신은 만능 생활 도우미입니다. {user_name}님의 최근 대화 내용을 분석하여 주요 관심사와 유용한 생활 팁을 정리한 보고서를 마크다운 형식으로 작성하세요."},
                {"role": "user", "content": f"{user_name}님의 일상생활 상담 분석 보고서 작성:\n\n{chat_data}"}
            ]
        )

        return jsonify({'status': 'success', 'report': response.choices[0].message.content})

    except Exception as e:
        print(f"[Daily Report Error] {e}")
        return jsonify({'error': '리포트 생성 중 오류가 발생했습니다.'}), 500