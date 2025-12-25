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
bp = Blueprint('learning_chat', __name__, url_prefix='/learning')

# --- 챗봇 환경 설정 ---
USER_NAME = "자유로움"
CHAT_TITLE = "효율적인 학습 및 시험 대비 챗봇"

# 시스템 페르소나 설정
SYSTEM_PROMPT = """
당신은 온라인 강의 추천, 시험 과목별 핵심 요약, 효율적인 공부법, 집중력 향상 팁, 특정 자격증 시험 대비 자료 등 사용자의 학습 효율을 높이고 성공적인 시험 준비를 위한 정보를 제공하는 '스마트하고 체계적인 학습 전략가' 챗봇입니다.
사용자 이름: {user_name}

[페르소나 & 역할]
1. 성격: 학습 목표 달성을 위한 효율적인 방법론을 제시하고, 사용자의 잠재력을 최대한 끌어낼 수 있도록 돕는 전략적인 조력자입니다.
2. 어조: 명료하고 실용적인 정보를 전달하며, 동기를 부여하고 긍정적인 학습 경험을 유도하는 전문적인 대화체를 사용합니다.
3. 주요 역할: 학습자의 상황을 분석하여 맞춤형 학습 계획 및 전략을 제시하고, 효과적인 자료 활용법과 시험 대비 팁을 제공합니다.
4. 답변 Role: 답변은 반드시 [공감 & 학습 목표 확인] → [효율 학습 핵심] → [단계별 전략 가이드] → [자기 점검 & 추가 자료] 순서로 구성되어야 합니다.

[답변 가이드라인]
1. 출력 형식: 답변 내용은 마크다운 형식(헤딩, 볼드, 목록)을 사용하여 가독성 높게 작성하며, 단계별 전략 가이드는 명확한 목록으로 제시합니다. 불필요한 이모지 사용은 지양합니다.

[범위 제한 및 거절 지침]
5. 역할 및 범위 제한 (필수): 당신은 오직 학습 전략, 공부법, 시험 정보, 집중력 향상 팁 등 학습 관련 정보만 제공합니다.
6. 범위 이탈 시 대응 (최우선): 문제의 정답 직접 제공, 시험 합격 보장, 타 분야 전문 상담(법률, 의료, 금융, 커리어), 개인의 학습 자료 작성 대행과 같이 전문적인 영역을 침범하는 질문이 들어오면 반드시 아래 거절 템플릿을 사용하여 단호하게 거절하십시오.
    * 거절 템플릿: "저는 효율적인 학습 및 시험 대비 챗봇으로서 [사용자가 요청한 주제]와 같은 문제 정답 제공이나 비학습 분야의 전문 상담에 대해서는 도움을 드릴 수 없습니다. 저는 오직 학습 전략 및 시험 대비 노하우에 대한 조언만 가능합니다. 다른 학습 관련 질문이 있으시다면 기꺼이 조언해 드리겠습니다."

[면책 조항]
7. 면책 조항: 답변의 마지막에 "⭐ 중요: 이 챗봇은 학습 정보와 전략을 제공하지만, 개인의 시험 합격이나 특정 학습 결과를 보장하지 않습니다. 제공된 정보를 바탕으로 꾸준히 노력하는 것이 중요합니다."라는 면책 조항을 포함합니다.
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
    print(f"[Learning] OpenAI Init Error: {e}")


# --- 1. 초기 안내 데이터 제공 (/learning/) ---
@bp.route('/')
def chat_usage():
    user_name = session.get('user_name', USER_NAME)
    user_id = session.get('user_id')

    chat_intro_html = f"""
        <div class="initial-text" style="margin-top: 5px;">
            <b>환영합니다!</b> {user_name}님의 스마트한 학습 동반자, '효율적인 학습 및 시험 대비' 챗봇입니다!
        </div>
        <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
            공부 계획 세우기부터 시험 직전 마무리 전략, 집중력 향상 비법, 그리고 특정 자격증 시험 정보까지! {user_name}님의 학습 목표 달성을 위한 모든 질문에 최적의 해답을 제시해 드립니다. 저와 함께 똑똑하게 공부하고 꿈을 이루세요!
        </div>
        <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
            <b>어떤 질문을 해야 할까요?</b>
            <ul>
            <li>"행정사 시험을 준비하고 있는데, 효율적인 암기법이 궁금해요."</li>
            <li>"수학 공부가 너무 어려운데, 개념을 쉽게 이해하는 방법이 있을까요?"</li>
            <li>"시험 한 달 전부터 어떻게 계획을 세워야 할까요?"</li>
            <li>"국가계약법 핵심 내용만 요약해 줄 수 있나요?"</li>
            </ul>
        </div>
        <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
            <span style="color: red; font-weight: bold;">⭐꼭 기억해주세요!</span>
            <p>이 챗봇은 학습 정보와 전략을 제공하지만, 개인의 시험 합격이나 특정 학습 결과를 보장하지 않습니다. <br>제공된 정보를 바탕으로 꾸준히 노력하는 것이 중요합니다.</p>
        </div><p>자, 이제 {user_name}님의 학습 고민을 들려주세요. 성장을 위한 여정을 응원합니다!</p>
        """

    return jsonify({
        "status": "success",
        "user_name": user_name,
        "is_logged_in": bool(user_id),
        "chat_title": CHAT_TITLE,
        "intro_html": chat_intro_html
    })


# --- 2. API 호출 및 하이브리드 저장 (/learning/ask) ---
@bp.route('/ask', methods=['POST'])
def ask():
    if client is None:
        return jsonify({'response': 'Error: OpenAI API Key missing.'}), 500

    current_user_id = session.get('user_id', 1)
    print(f"[Learning/Ask] Processing for User ID: {current_user_id}")

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
                category='learning',
                question=user_message,
                answer=ai_response,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(new_log)
            db.session.commit()
            sql_id = new_log.id

            # 2. MongoDB 저장 (데이터베이스 객체 비교 시 is not None 필수)
            mongodb = getattr(current_app, 'mongodb', None)
            if mongodb is not None:
                try:
                    mongodb.chat_history.insert_one({
                        "sql_id": sql_id,
                        "user_id": current_user_id,
                        "category": "learning",
                        "question": user_message,
                        "answer": ai_response,
                        "timestamp": datetime.now(timezone.utc)
                    })
                except Exception as mongo_err:
                    print(f"[Learning Mongo Error] {mongo_err}")

            # 3. Vector DB 저장 (명시적 None 비교)
            vector_db = getattr(current_app, 'vector_db', None)
            if vector_db is not None:
                try:
                    vector_db.add(
                        documents=[user_message],
                        ids=[f"learning_{sql_id}"],
                        metadatas=[{"user_id": current_user_id, "category": "learning"}]
                    )
                except Exception as vec_err:
                    print(f"[Learning Vector Error] {vec_err}")

            print(f"[Learning] Hybrid Storage Success: User {current_user_id}")

        except Exception as db_err:
            db.session.rollback()
            print(f"[Learning Storage Error] {db_err}")

        return jsonify({'status': 'success', 'response': ai_response})

    except Exception as e:
        print(f"[Learning API Error] {e}")
        return jsonify({'response': '서버 통신 오류가 발생했습니다.'}), 500


# --- 3. 리포트 생성 함수 (/learning/report) ---
@bp.route('/report', methods=['GET'])
def generate_report():
    user_id = session.get('user_id', 1)

    try:
        history = ChatLog.query.filter_by(user_id=user_id, category='learning') \
            .order_by(ChatLog.created_at.desc()) \
            .limit(5).all()

        if not history:
            return jsonify({'error': '상담 내역이 부족하여 리포트를 생성할 수 없습니다.'}), 404

        chat_data = "\n".join([f"Q: {h.question}\nA: {h.answer}" for h in reversed(history)])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "당신은 교육 전략 전문가입니다. 상담 내용을 분석하여 사용자의 학습 패턴 진단과 효율적인 성취를 위한 학습 로드맵을 마크다운 형식으로 작성하세요."},
                {"role": "user", "content": f"학습 상담 분석 리포트 작성:\n\n{chat_data}"}
            ]
        )

        return jsonify({'status': 'success', 'report': response.choices[0].message.content})

    except Exception as e:
        print(f"[Learning Report Error] {e}")
        return jsonify({'error': '리포트 생성 중 오류가 발생했습니다.'}), 500