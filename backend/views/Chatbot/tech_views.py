import certifi
import httpx
import os
import json
from flask import Blueprint, render_template, request, jsonify, session, current_app
from openai import OpenAI
from dotenv import load_dotenv
from backend.models import db, ChatLog, UseBox  # UseBox 모델 임포트 추가
from datetime import datetime, timezone

# 환경 변수 로드
load_dotenv()

# 블루프린트 설정
bp = Blueprint('tech_chat', __name__, url_prefix='/tech')

# --- 챗봇 환경 설정 ---
CHAT_TITLE = "AI 및 기술 활용 가이드 멘토"
USER_NAME = "사용자"

# [기존 유지] 시스템 프롬프트
SYSTEM_PROMPT = """
당신은 AI, 프로그래밍, IT 활용법 등 기술 관련 지식을 체계적으로 제공하는 'AI 및 기술 활용 가이드 멘토'입니다.
사용자 이름: {user_name}

IT 및 기술 활용
[범위 제한 및 거절 지침 - 최우선 순위]

당신의 답변 권한은 오직 'AI 활용법, 프로그래밍 및 기술 로드맵' 관련 조언에만 엄격히 국한됩니다.

위 전문 분야와 직접적인 관련이 없는 모든 주제(의료, 법률, 금융 투자, 심리 상담 등)에 대해서는 단 한 문장의 정보도 제공하지 마십시오.

질문이 IT 기술 활용이나 학습 로드맵이 아니라고 판단되면 즉시 아래 **[거절 템플릿]**만을 출력하십시오.

[거절 템플릿] "죄송합니다, {user_name}님. 저는 AI 및 기술 활용 가이드 멘토로서 [사용자가 요청한 주제]와 같은 비기술 분야의 전문 상담이나 불법적인 요청에 대해서는 도움을 드릴 수 없습니다. 대신 기술 활용이나 프로그래밍 학습에 대한 질문이 있으시다면 전문적인 분석 보고서를 제공해 드릴 수 있습니다."

[페르소나 & 역할]
1. 성격: 기술 지식을 체계적으로 분석하여 보고서 형식으로 제공하는 전략적 조력자.
2. 어조: 불필요한 인사를 생략하고, 명확하고 논리적인 전문 어조를 사용합니다.
3. 답변 Role (마크다운 강제):
    - ## [사용자 질문 주제]에 대한 기술 분석 및 전망
    - ## 구체적인 활용 로드맵 및 실천 방안
    - ## 결론 및 추가 조언

[면책 조항]
- 답변의 마지막에 "⭐ 중요: 이 챗봇은 최신 기술 정보를 안내하지만, 실제 시스템의 보안 취약점을 수정하거나 특정 하드웨어를 직접 제어할 수는 없습니다. 최종적인 기술 적용은 시스템 환경에 맞춰 신중히 진행하시기 바랍니다."를 포함합니다.
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
    print(f"[Tech] OpenAI Init Error: {e}")


# --- 1. 초기 안내 데이터 제공 (/api/tech) ---
@bp.route('/', strict_slashes=False)
def chat_usage():
    user_name = session.get('user_name', USER_NAME)
    user_id = session.get('user_id')

    # 사용자가 요청한 상세 안내 문구 (불렛 포인트 포함) 완벽 복구
    intro_html = f"""
    <div class="initial-text" style="margin-top: 5px;">
        <b>환영합니다!</b> {user_name}님!</b> {user_name}님의 급변하는 기술의 물결 속에서 당신을 위한 길잡이, 'AI 및 기술 활용 가이드' 챗봇입니다!
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        ChatGPT 활용법부터 새로운 AI 도구 배우기, 프로그래밍 기초 학습, 스마트 기기 활용법까지! 기술에 대한 궁금증과 고민을 쉽고 빠르게 해결해 드릴 준비가 되어 있습니다.
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <b>어떤 질문을 해야 할까요?</b>
        <ul>
            <li>"ChatGPT를 업무에 활용하고 싶은데, 어떤 질문부터 시작해야 할까요?"</li>
            <li>"파이썬(Python)으로 데이터 분석을 시작하려면 뭘 공부해야 하나요?"</li>
        </ul>
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <span style="color: red; font-weight: bold;">⭐꼭 기억해주세요!</span>
        <p>이 챗봇은 최신 기술 정보와 활용법을 안내해 드리지만, 실제 코딩 오류를 수정하거나 특정 하드웨어를 <br>직접 제어할 수는 없습니다. 언제든 궁금한 점을 편하게 물어보세요!</p>
    </div><p>자, 이제 {user_name}님의 기술 관련 질문을 들려주세요. 제가 전문적인 분석으로 답해 드릴게요!</p>
    """

    return jsonify({
        "status": "success",
        "user_name": user_name,
        "is_logged_in": bool(user_id),
        "chat_title": CHAT_TITLE,
        "intro_html": intro_html
    })


# --- 2. API 호출 및 하이브리드 저장 (/api/tech/ask) ---
@bp.route('/ask', methods=['POST'], strict_slashes=False)
def ask():
    if client is None:
        return jsonify({'response': 'Error: OpenAI API Key missing.'}), 500

    current_user_id = session.get('user_id', 1)

    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'response': '메시지를 입력해주세요.'}), 400

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=2048,
            temperature=0.1
        )

        gpt_response = response.choices[0].message.content.strip()

        # --- 하이브리드 저장 로직 (최신 UseBox 방식 적용) ---
        try:
            # 1. UseBox(권한) 확인 및 자동생성 - 테크 가이드는 ai_id=8
            TECH_AI_ID = 8
            usebox = UseBox.query.filter_by(user_id=current_user_id, ai_id=TECH_AI_ID).first()

            if not usebox:
                usebox = UseBox(user_id=current_user_id, ai_id=TECH_AI_ID)
                db.session.add(usebox)
                db.session.commit()

            # 2. SQL 저장 (수정된 DB 구조 반영: usebox_id 사용)
            new_log = ChatLog(
                usebox_id=usebox.use_id,
                question=user_message,
                answer=gpt_response,
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
                        "category": "tech",
                        "question": user_message,
                        "answer": gpt_response,
                        "timestamp": datetime.now(timezone.utc)
                    })
                    print(">>> [SUCCESS] Tech data saved to MongoDB Atlas!")
                except Exception as mongo_err:
                    print(f"[Tech Mongo Error] {mongo_err}")

            # 4. Vector DB 저장
            vector_db = getattr(current_app, 'vector_db', None)
            if vector_db is not None:
                try:
                    vector_db.add(
                        documents=[user_message],
                        ids=[f"tech_{sql_id}"],
                        metadatas=[{"user_id": current_user_id, "category": "tech"}]
                    )
                except Exception as vec_err:
                    print(f"[Tech Vector Error] {vec_err}")

        except Exception as db_err:
            db.session.rollback()
            print(f"[Tech Storage Error] {db_err}")

        return jsonify({'status': 'success', 'response': gpt_response})

    except Exception as e:
        print(f"[Tech API Error] {e}")
        return jsonify({'response': '서버 통신 오류가 발생했습니다.'}), 500


# --- 3. 리포트 생성 함수 (/api/tech/report) ---
@bp.route('/report', methods=['GET'], strict_slashes=False)
def generate_report():
    user_id = session.get('user_id', 1)

    try:
        # UseBox 조인을 통해 테크(ai_id=8) 기록만 필터링
        history = ChatLog.query.join(UseBox).filter(
            UseBox.user_id == user_id,
            UseBox.ai_id == 8
        ).order_by(ChatLog.created_at.desc()).limit(5).all()

        if not history:
            return jsonify({'error': '기술 상담 내역이 부족합니다.'}), 404

        chat_data = "\\n".join([f"Q: {h.question}\\nA: {h.answer}" for h in reversed(history)])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "IT 기술 전략가입니다. 전문 분석 리포트를 작성하세요."},
                {"role": "user", "content": f"기술 활용 상담 분석 리포트 작성:\\n\\n{chat_data}"}
            ]
        )

        return jsonify({'status': 'success', 'report': response.choices[0].message.content})

    except Exception as e:
        print(f"[Tech Report Error] {e}")
        return jsonify({'error': '리포트 생성 중 오류가 발생했습니다.'}), 500