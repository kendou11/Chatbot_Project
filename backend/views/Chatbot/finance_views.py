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
bp = Blueprint('finance_chat', __name__, url_prefix='/finance')

# --- 챗봇 환경 설정 ---
USER_NAME = "자유로움"
CHAT_TITLE = "재테크 및 금융 컨설팅 챗봇"

# 시스템 페르소나 설정
SYSTEM_PROMPT = """
당신은 사용자의 재산을 효율적으로 관리하고 증식하기 위한 맞춤형 컨설팅과 정보를 제공하는 '현명하고 신뢰할 수 있는 금융 멘토' 챗봇입니다.
사용자 이름: {user_name}

[페르소나 & 역할]
1. 성격: 복잡한 금융 정보를 쉽고 명확하게 설명하며, 사용자가 합리적인 재정 결정을 내리도록 돕는 신뢰감 있는 멘토입니다.
2. 어조: 객관적이고 정확한 정보를 기반으로, 사용자 상황에 맞는 실용적인 조언을 제시하는 전문적인 대화체를 사용합니다.
3. 주요 역할: 주식, 부동산, 가상자산 등 투자 정보, 은행 상품 비교, 대출, 세금, 연금, 절약 노하우 등 재정 목표 달성에 필요한 정보를 제공합니다. 리스크 관리를 강조하여 재정 건전성 유지에 기여합니다.
4. 답변 Role: 답변은 반드시 [공감 & 목표 확인] → [핵심 원리 & 리스크] → [단계별 실천 가이드] → [추가 정보 & 전문가 제안] 순서로 구성되어야 합니다.

[답변 가이드라인]
1. 출력 형식: 답변 내용은 마크다운 형식(헤딩, 볼드, 목록)을 사용하여 가독성 높게 작성하며, 단계별 실천 가이드는 명확한 목록으로 제시합니다.

[범위 제한 및 거절 지침]
5. 역할 및 범위 제한 (필수): 당신은 오직 금융 일반 정보, 재테크 전략, 투자 정보 제공에 국한됩니다.
6. 범위 이탈 시 대응: 개별 투자 종목의 추천 및 매매 시점 권유, 법률 자문(상속, 소송), 세무사나 회계사의 전문 영역(세금 신고 대리, 복잡한 세금 계산), 심리 상담과 같이 전문적인 영역을 침범하는 질문이 들어오면 반드시 아래 거절 템플릿을 사용하여 단호하게 거절하십시오.
    * 거절 템플릿: "저는 금융 컨설팅 챗봇으로서 [사용자가 요청한 주제]와 같은 전문 영역에 대해서는 직접적인 도움을 드릴 수 없습니다. 저는 오직 객관적인 재정 정보와 전략을 안내해 드릴 수 있습니다. 다른 재테크 관련 질문이 있으시다면 기꺼이 조언해 드리겠습니다."

[면책 조항]
7. 면책 조항: 답변의 마지막에 "⭐ 중요: 모든 투자에는 위험이 따르며, 챗봇의 정보는 참고용일 뿐입니다. 최종 투자 결정은 반드시 사용자 본인의 신중한 판단과 책임 하에 이루어져야 합니다."라는 면책 조항을 포함합니다.
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
    print(f"[Finance] OpenAI Init Error: {e}")


# --- 1. 초기 안내 데이터 제공 (/finance/) ---
@bp.route('/')
def chat_usage():
    user_name = session.get('user_name', USER_NAME)
    user_id = session.get('user_id')

    chat_intro_html = f"""
    <div class="initial-text" style="margin-top: 5px;">
        <b>환영합니다!</b> 안녕하세요! {user_name}님의 현명한 자산 관리를 돕는 '재테크 및 금융 컨설팅' 챗봇입니다!
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        투자의 첫 걸음부터 복잡한 금융 상품 이해, 절세 전략, 노후 준비까지! {user_name}님의 재정 목표에 맞춰 필요한 금융 정보와 실질적인 조언을 드릴 준비가 되어 있습니다. <br>어려운 금융, 이제 저와 함께 쉽게 접근해보세요!
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <b>어떤 질문을 해야 할까요?</b>
        <ul>
            <li>"사회 초년생인데 월급 관리와 투자를 어떻게 시작해야 할까요?"</li>
            <li>"내집 마련을 위해 종잣돈을 모으고 싶은데, 효율적인 방법이 있을까요?"</li>
            <li>"ISA 계좌가 무엇이고 어떻게 활용할 수 있나요?"</li>
            <li>"요즘 유망하다는 산업 분야에 투자하고 싶은데, 관련 정보가 궁금해요."</li>
        </ul>
    </div>
    <div class="initial-text" style="margin-top: 10px; margin-bottom: 10px;">
        <span style="color: red; font-weight: bold;">꼭 기억해주세요!</span>
        <p>이 챗봇은 금융 정보와 조언을 제공하지만, 개별 투자 결정이나 법적 효력을 가진 금융 상품 가입을 직접 권유하지 않습니다. 모든 투자에는 위험이 따르며, <br>최종 결정은 사용자 본인의 판단에 따라야 합니다.</p>
    </div><p>자, 이제 {user_name}님의 금융 고민을 들려주세요. 함께 해결책을 찾아볼게요!</p>
    """

    return jsonify({
        "status": "success",
        "user_name": user_name,
        "is_logged_in": bool(user_id),
        "chat_title": CHAT_TITLE,
        "intro_html": chat_intro_html
    })


# --- 2. API 호출 및 하이브리드 저장 (/finance/ask) ---
@bp.route('/ask', methods=['POST'])
def ask():
    if client is None:
        return jsonify({'response': 'Error: OpenAI API Key missing.'}), 500

    current_user_id = session.get('user_id', 1)
    print(f"[Finance/Ask] Processing for User ID: {current_user_id}")

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
                category='finance',
                question=user_message,
                answer=ai_response,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(new_log)
            db.session.commit()
            sql_id = new_log.id

            # 2. MongoDB 저장 (명시적 None 비교 적용)
            mongodb = getattr(current_app, 'mongodb', None)
            if mongodb is not None:
                try:
                    mongodb.chat_history.insert_one({
                        "sql_id": sql_id,
                        "user_id": current_user_id,
                        "category": "finance",
                        "question": user_message,
                        "answer": ai_response,
                        "timestamp": datetime.now(timezone.utc)
                    })
                except Exception as mongo_err:
                    print(f"[Finance Mongo Error] {mongo_err}")

            # 3. Vector DB 저장 (명시적 None 비교 적용)
            vector_db = getattr(current_app, 'vector_db', None)
            if vector_db is not None:
                try:
                    vector_db.add(
                        documents=[user_message],
                        ids=[f"finance_{sql_id}"],
                        metadatas=[{"user_id": current_user_id, "category": "finance"}]
                    )
                except Exception as vec_err:
                    print(f"[Finance Vector Error] {vec_err}")

            print(f"[Finance] Hybrid Storage Success: User {current_user_id}")

        except Exception as db_err:
            db.session.rollback()
            # 이모지 제거하여 인코딩 에러 방지
            print(f"[Finance Storage Error] {db_err}")

        return jsonify({'status': 'success', 'response': ai_response})

    except Exception as e:
        # 이모지 제거하여 인코딩 에러 방지
        print(f"[Finance API Error] {e}")
        return jsonify({'response': '서버 통신 오류가 발생했습니다.'}), 500


# --- 3. 리포트 생성 함수 (/finance/report) ---
@bp.route('/report', methods=['GET'])
def generate_report():
    user_id = session.get('user_id', 1)

    try:
        history = ChatLog.query.filter_by(user_id=user_id, category='finance') \
            .order_by(ChatLog.created_at.desc()) \
            .limit(5).all()

        if not history:
            return jsonify({'error': '분석할 상담 내역이 부족합니다.'}), 404

        chat_data = "\n".join([f"Q: {h.question}\nA: {h.answer}" for h in reversed(history)])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "당신은 전문 자산 관리사입니다. 사용자의 상담 내용을 분석하여 재정 상태 진단과 맞춤형 투자 방향을 요약한 보고서를 마크다운 형식으로 작성하세요."},
                {"role": "user", "content": f"금융 상담 분석 보고서 작성:\n\n{chat_data}"}
            ]
        )

        return jsonify({'status': 'success', 'report': response.choices[0].message.content})

    except Exception as e:
        print(f"[Finance Report Error] {e}")
        return jsonify({'error': '리포트 생성 중 오류가 발생했습니다.'}), 500