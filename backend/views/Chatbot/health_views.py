import certifi
import httpx
import os
import json
from flask import Blueprint, render_template, request, jsonify, session, current_app
from openai import OpenAI
from dotenv import load_dotenv
from backend.models import db, ChatLog
from datetime import datetime, timezone

load_dotenv()

# 블루프린트 생성
bp = Blueprint('health_chat', __name__, url_prefix='/health')

# --- 챗봇 환경 설정 ---
USER_NAME = "자유로움"
CHAT_TITLE = "개인 맞춤형 건강 코치"

# [기존 유지] 시스템 페르소나 설정
SYSTEM_PROMPT = """
당신은 사용자의 건강 목표 달성을 돕는 스마트하고 동기 부여하는 '건강 코치' 챗봇입니다.
사용자 이름: {user_name}

[페르소나 & 역할]
1. 성격: 과학적 근거를 바탕으로 명쾌하게 조언하며, 사용자가 꾸준히 건강 목표를 달성하도록 동기를 부여하는 긍정적인 코치입니다.
2. 어조: 명료하고 실용적인 정보를 전달하며, 사용자 맞춤형 솔루션을 제안하는 적극적인 대화체를 사용합니다.
3. 주요 역할: 사용자의 건강 목표(다이어트, 운동 루틴, 영양제 정보 등)를 이해하고, 맞춤형 식단 및 운동 계획을 제시하며, 신체 건강 및 영양에 대한 실질적인 가이드를 제공하는 전문 코치 역할을 수행합니다.

[답변 가이드라인]
1. 답변 Role: [공감 & 목표 확인] → [핵심 원리 & 중요성] → [맞춤형 실천 계획] → [지속 관리 & 전문가 제안] 순서로 구성하여 답변합니다.
2. 출력 형식: 답변 내용은 마크다운 형식(볼드, 목록)을 사용하여 가독성 높게 작성합니다.

[범위 이탈 시 대응]
4. 역할 및 범위 제한 (필수): 당신은 신체 건강, 운동, 식단, 영양, 수면 위생, 일반적인 질병 예방을 위한 생활 습관과 관련된 조언만을 제공합니다.
5. 범위 이탈 시 대응: 심리 상담, 정신 질환 진단, 법률, 금융, 또는 구체적인 질병 치료 및 처방과 같이 전문 의료진이 담당해야 하는 질문이 들어오면 반드시 아래 거절 템플릿을 사용하여 단호하게 거절하십시오.
    * 거절 템플릿: "저는 개인 맞춤형 건강 관리 코치로서 [사용자가 요청한 주제]와 같은 심리 상담이나 전문적인 의료 진단/처방 분야에 대해서는 도움을 드릴 수 없습니다. 저는 오직 신체 건강 및 영양에 대한 조언만 가능합니다. 다른 건강 관련 질문이 있으시다면 기꺼이 조언해 드리겠습니다."

[면책 조항]
3. 면책 조항: 답변의 마지막에 "⭐ 중요: 저는 AI 건강 코치이며, 의학적 진단이나 처방을 할 수 없습니다. 질병 치료나 심각한 건강 문제는 반드시 전문 의료진과 상담하세요."라는 면책 조항을 포함합니다.
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
    print(f"[Health] OpenAI Init Error: {e}")


# --- 1. 초기 안내 데이터 제공 (/health/) ---
@bp.route('/')
def chat_usage():
    display_name = session.get('user_name', USER_NAME)
    user_id = session.get('user_id')

    chat_intro_html = f"""
    <div class="initial-text" style="margin-top: 5px;">
        <b>환영합니다!</b> 안녕하세요! {display_name}님의 건강을 위한 맞춤형 가이드, '개인 맞춤형 건강 관리' 챗봇입니다!
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        체중 감량, 근력 증진, 만성 질환 관리, 영양 균형 등 구체적인 건강 목표에 맞춰 식단, 운동, 생활 습관에 대한 실질적인 조언과 정보를 제공해 드립니다. 지금 바로 당신의 건강 고민을 저와 나눠보세요!
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <b>어떤 질문을 해야 할까요?</b>
        <ul>
            <li>"체중 감량을 위한 식단과 운동 루틴을 추천해 줄 수 있나요?"</li>
            <li>"혈압 관리를 위해 어떤 음식을 먹는 게 좋을까요?"</li>
            <li>"요즘 피곤한데 활력을 주는 영양제가 있을까요?"</li>
            <li>"집에서 간단하게 할 수 있는 유산소 운동 좀 알려주세요."</li>
        </ul>
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <span style="color: red; font-weight: bold;">꼭 기억해주세요!</span>
        <p>이 챗봇은 건강 정보와 맞춤형 조언을 제공하지만, 의학적 진단이나 처방을 대체할 수 없습니다. <br>질병 치료나 심각한 건강 문제는 반드시 전문 의료진과 상담하시길 권장합니다.</p>
    </div><p>자, 이제 {display_name}님의 건강 고민을 들려주세요. 활기찬 여정을 응원합니다!</p>
    """

    return jsonify({
        "status": "success",
        "user_name": display_name,
        "is_logged_in": bool(user_id),
        "chat_title": CHAT_TITLE,
        "intro_html": chat_intro_html
    })


# --- 2. API 호출 및 하이브리드 저장 (/health/ask) ---
@bp.route('/ask', methods=['POST'])
def ask():
    if client is None:
        return jsonify({'response': 'Error: OpenAI API Key missing.'}), 500

    current_user_id = session.get('user_id', 1)
    print(f"[Health/Ask] Processing for User ID: {current_user_id}")

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
            temperature=0.7
        )

        ai_response = response.choices[0].message.content.strip()

        # --- 하이브리드 저장 로직 (SQL + MongoDB + Vector DB) ---
        try:
            # 1. SQL 저장
            new_log = ChatLog(
                user_id=current_user_id,
                category='health',
                question=user_message,
                answer=ai_response,
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
                        "category": "health",
                        "question": user_message,
                        "answer": ai_response,
                        "timestamp": datetime.now(timezone.utc)
                    })
                except Exception as mongo_err:
                    print(f"[Health Mongo Error] {mongo_err}")

            # 3. Vector DB 저장 (is not None 필수)
            vector_db = getattr(current_app, 'vector_db', None)
            if vector_db is not None:
                try:
                    vector_db.add(
                        documents=[user_message],
                        ids=[f"health_{sql_id}"],
                        metadatas=[{"user_id": current_user_id, "category": "health"}]
                    )
                except Exception as vec_err:
                    print(f"[Health Vector Error] {vec_err}")

            print(f"[Health] Hybrid Storage Success: User {current_user_id}")

        except Exception as db_err:
            db.session.rollback()
            print(f"[Health Storage Error] {db_err}")

        return jsonify({'status': 'success', 'response': ai_response})

    except Exception as e:
        print(f"[Health API Error] {e}")
        return jsonify({'response': '서버 통신 오류가 발생했습니다.'}), 500


# --- 3. 리포트 생성 함수 (/health/report) ---
@bp.route('/report', methods=['GET'])
def generate_report():
    user_id = session.get('user_id', 1)

    try:
        history = ChatLog.query.filter_by(user_id=user_id, category='health') \
            .order_by(ChatLog.created_at.desc()) \
            .limit(5).all()

        if not history:
            return jsonify({'error': '분석할 건강 상담 내역이 부족합니다.'}), 404

        chat_data = "\n".join([f"Q: {h.question}\nA: {h.answer}" for h in reversed(history)])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "당신은 건강 관리 전문가입니다. 상담 내역을 바탕으로 사용자의 건강 상태 요약 및 생활 습관 개선 권고안을 마크다운 형식으로 작성하세요."},
                {"role": "user", "content": f"건강 상담 분석 리포트 작성:\n\n{chat_data}"}
            ]
        )

        return jsonify({'status': 'success', 'report': response.choices[0].message.content})

    except Exception as e:
        print(f"[Health Report Error] {e}")
        return jsonify({'error': '리포트 생성 중 오류가 발생했습니다.'}), 500

# [테스트용] 벡터 DB 저장 내용 확인 API
@bp.route('/debug/vector')
def debug_vector():
    # 1. 현재 앱에 할당된 객체 확인
    vdb = current_app.vector_db
    if vdb is None:
        return jsonify({"status": "error", "message": "Vector DB 객체가 None입니다."})

    try:
        # 2. 현재 컬렉션의 실제 데이터 개수와 샘플 데이터 추출
        count = vdb.count()
        peek = vdb.peek(limit=5)  # 실제 데이터 내용 5개 확인

        return jsonify({
            "status": "success",
            "collection_name": vdb.name,  # 현재 연결된 컬렉션 이름 확인
            "total_count": count,
            "sample_data": peek
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})