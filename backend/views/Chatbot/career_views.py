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
bp = Blueprint('career_chat', __name__, url_prefix='/career')

# --- 챗봇 환경 설정 ---
# [수정] 고정된 "자유로움" 제거 및 기본값 설정
DEFAULT_NAME = "사용자"
CHAT_TITLE = "커리어 개발 및 취업 준비 챗봇"

# [수정] SYSTEM_PROMPT 내의 설명도 동적으로 구성하기 위해 f-string이 아닌 템플릿 형태로 유지
SYSTEM_PROMPT = """
당신은 사용자의 경력 발전과 성공적인 취업을 위한 실질적인 정보와 전략을 제공하는 '스마트하고 전략적인 커리어 멘토' 챗봇입니다.
사용자 이름: {user_name}

[범위 제한 및 거절 지침 - 최우선 순위]

당신의 답변 권한은 오직 '진로 탐색, 자소서 및 면접 전략' 관련 조언에만 엄격히 국한됩니다.

위 전문 분야와 직접적인 관련이 없는 모든 주제(건강 증상, 법적 분쟁, 금융 투자, 기술 수리 등)에 대해서는 단 한 문장의 정보도 제공하지 마십시오.

질문이 커리어 설계나 취업 준비가 아니라고 판단되면 즉시 아래 **[거절 템플릿]**만을 출력하십시오.

[거절 템플릿] "죄송합니다, {user_name}님. 저는 커리어 및 취업 멘토로서 [사용자가 요청한 주제]와 같은 비직무 분야의 전문적인 상담에 대해서는 도움을 드릴 수 없습니다. 대신 커리어 설계나 면접 준비 등 취업과 관련된 질문이 있으시다면 기꺼이 조언해 드리겠습니다."

[페르소나 & 역할]
1. 성격: 냉철한 시장 분석과 따뜻한 격려를 동시에 제공하는 전문 컨설턴트입니다.
2. 어조: 전문적이고 신뢰감을 주는 비즈니스 어조를 사용하되, 구체적인 행동 지침을 제시합니다.
3. 주요 역할: 직무 분석, 이력서/자기소개서 피드백, 면접 전략, 경력 로드맵 설계 등 커리어 전반에 걸친 가이드를 제공합니다.
4. 답변 Role: 답변은 반드시 [상황 공감] → [현 직무/시장 트렌드 분석] → [단계별 실행 전략] → [전문가 한마디] 순서로 구성하세요.

[출력 형식]
- 마크다운(헤딩, 볼드, 목록)을 활용하여 가독성을 극대화하세요.
- 추상적인 조언보다는 '지금 당장 해야 할 일' 위주로 구체적으로 작성하세요.
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
    print(f"[Career] OpenAI Init Error: {e}")


# --- 1. 초기 안내 프롬프트 제공 (/career/) ---
@bp.route('/')
def chat_usage():
    # [수정] 실시간 닉네임 확보: user_nickname -> user_name -> 기본값 순서
    user_name = session.get('user_nickname') or session.get('user_name') or DEFAULT_NAME
    user_id = session.get('user_id')

    # [수정] intro_html 내의 모든 고정 이름을 {user_name} 변수로 교체
    chat_intro_html = f"""
    <div class="initial-text" style="margin-top: 5px;">
        <b>환영합니다!</b> {user_name}님! {user_name}님의 성공적인 내일을 설계하는 '커리어 및 취업 준비' 챗봇입니다!
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        원하는 직무로의 이직, 첫 취업의 문턱, 혹은 나만의 경력 로드맵 설정까지! <b>{user_name}님</b>의 소중한 꿈이 실현될 수 있도록 실질적인 전략을 함께 고민해 드릴게요.
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <b>이런 고민이 있으신가요?</b>
        <ul>
            <li>"데이터 분석가 직무로 신입 지원하려고 하는데, 포트폴리오에 꼭 포함되어야 할 내용은?"</li>
            <li>"경력 3년 차 이직을 준비 중입니다. 연봉 협상에서 유리한 전략이 궁금해요."</li>
            <li>"압박 면접 질문에 당황하지 않고 대처하는 방법이 있을까요?"</li>
            <li>"비전공자가 IT 기획자로 커리어를 전환하려면 무엇부터 준비해야 할까요?"</li>
        </ul>
    </div>
    <p style="margin-top: 10px;">자, 이제 <b>{user_name}님</b>의 커리어 고민을 들려주세요. 제가 함께 전략을 세워보겠습니다!</p>
    """

    return jsonify({
        "status": "success",
        "user_name": user_name,
        "is_logged_in": bool(user_id),
        "chat_title": CHAT_TITLE,
        "intro_html": chat_intro_html
    })


# --- 2. 질문 처리 및 하이브리드 저장 (/career/ask) ---
@bp.route('/ask', methods=['POST'])
def ask():
    if client is None:
        return jsonify({'response': 'OpenAI API Key is missing.'}), 500

    current_user_id = session.get('user_id', 1)
    # [수정] 질문 처리 시에도 실시간 닉네임 사용
    user_name = session.get('user_nickname') or session.get('user_name') or DEFAULT_NAME

    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'response': '메시지를 입력해주세요.'}), 400

        # [수정] SYSTEM_PROMPT에 실시간 user_name 주입
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

        # --- 저장 로직 ---
        try:
            CAREER_AI_ID = 5
            usebox = UseBox.query.filter_by(user_id=current_user_id, ai_id=CAREER_AI_ID).first()

            if not usebox:
                usebox = UseBox(user_id=current_user_id, ai_id=CAREER_AI_ID)
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
                        "category": "career",
                        "question": user_message,
                        "answer": ai_response,
                        "timestamp": datetime.now(timezone.utc)
                    })
                except Exception as mongo_err:
                    print(f"[Career Mongo Error] {mongo_err}")

            vector_db = getattr(current_app, 'vector_db', None)
            if vector_db is not None:
                try:
                    vector_db.add(
                        documents=[user_message],
                        ids=[f"career_{sql_id}"],
                        metadatas=[{"user_id": current_user_id, "category": "career"}]
                    )
                except Exception as vec_err:
                    print(f"[Career Vector Error] {vec_err}")

        except Exception as db_err:
            db.session.rollback()
            print(f"[Career Storage Error] {db_err}")

        return jsonify({'status': 'success', 'response': ai_response})

    except Exception as e:
        print(f"[Career API Error] {e}")
        return jsonify({'response': '서버 통신 오류가 발생했습니다.'}), 500


# --- 3. 리포트 생성 (/career/report) ---
@bp.route('/report', methods=['GET'])
def generate_report():
    user_id = session.get('user_id', 1)
    # [수정] 리포트 생성 시에도 사용자 이름을 반영할 수 있도록 변수 확보
    user_name = session.get('user_nickname') or session.get('user_name') or DEFAULT_NAME

    try:
        history = ChatLog.query.join(UseBox).filter(
            UseBox.user_id == user_id,
            UseBox.ai_id == 5
        ).order_by(ChatLog.created_at.desc()).limit(5).all()

        if not history:
            return jsonify({'error': '상담 내역이 부족합니다.'}), 404

        chat_data = "\n".join([f"Q: {h.question}\nA: {h.answer}" for h in reversed(history)])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": f"당신은 커리어 컨설팅 전문가입니다. {user_name}님의 상담 내용을 분석하여 역량 강점과 향후 실행 과제를 요약한 리포트를 마크다운 형식으로 작성하세요."},
                {"role": "user", "content": f"{user_name}님의 커리어 상담 분석 리포트 작성:\n\n{chat_data}"}
            ]
        )

        return jsonify({'status': 'success', 'report': response.choices[0].message.content})

    except Exception as e:
        print(f"[Career Report Error] {e}")
        return jsonify({'error': '리포트 생성 중 오류가 발생했습니다.'}), 500