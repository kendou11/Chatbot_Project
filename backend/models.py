from datetime import datetime, timezone
from enum import IntEnum

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    # 유저DB
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)          # 유저일련번호
    user_email = db.Column(db.String(255), unique=True, nullable=True)             # 로그인 이메일
    user_password = db.Column(db.String(255), nullable=True)                       # 비밀번호 (secret_key 적용 예정)
    user_nickname = db.Column(db.String(50), unique=True, nullable=False)          # 닉네임, 기본값 'user'는 애플리케이션 레벨에서 처리 권장
    user_image = db.Column(db.String(500), nullable=True, default="기본이미지")      # 프로필 사진 경로
    user_birthdate = db.Column(db.Date, nullable=True)                             # 생년월일
    user_delete = db.Column(db.Boolean, nullable=False, default=False)             # 유저 유지(삭제 여부 플래그, 0이면 존재 1이면 삭제)
    user_is_social = db.Column(db.Boolean, nullable=False, default=False)          # 소셜 가능 여부(0이면 로컬 1이면 소셜)
    user_money = db.Column(db.Integer, nullable=False, default=0)                  # 가진 돈 금액
    user_start = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))   # 유저 생성 날짜

    def __repr__(self):
        return f"<User {self.user_id} {self.user_email}>"

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_email": self.user_email,
            "user_nickname": self.user_nickname,
            "user_image": self.user_image,
            "user_birthdate": self.user_birthdate.isoformat() if self.user_birthdate else None,
            "user_delete": self.user_delete,
            "user_is_social": self.user_is_social,
            "user_money": self.user_money,
            "user_start": self.user_start.isoformat() if self.user_start else None,
        }



class Social(db.Model):
    __tablename__ = "social"

    # 소셜DB
    social_id = db.Column(db.Integer, primary_key=True, autoincrement=True)             # 소셜 일련번호
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)      # 유저 일련번호 (FK -> user.user_id)
    social_provider = db.Column(db.String(50), nullable=False)                          # 소셜 종류 (카카오 / 네이버 / 구글 등)
    social_provider_id = db.Column(db.String(225), nullable=False)                      # 소셜 제공 아이디
    social_email = db.Column(db.String(255), nullable=True)                             # 소셜 제공 이메일
    social_image = db.Column(db.String(500), nullable=True)                             # 소셜 제공 이미지
    social_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))      # 소셜 로그인 생성 시간
    social_last_login = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)) # 소셜 마지막 로그인 시간

    # 관계: Social → User (N:1)
    user = db.relationship("User",backref=db.backref("social_accounts", lazy=True),lazy=True,)

    def __repr__(self):
        return f"<Social {self.social_id} {self.social_provider} user={self.user_id}>"

    def to_dict(self):
        return {
            "social_id": self.social_id,
            "user_id": self.user_id,
            "social_provider": self.social_provider,
            "social_provider_id": self.social_provider_id,
            "social_email": self.social_email,
            "social_image": self.social_image,
            "social_date": self.social_date.isoformat() if self.social_date else None,
            "social_last_login": self.social_last_login.isoformat() if self.social_last_login else None,
        }




#enum 사용하기 위한 객체
class PayMethod(IntEnum):
    CARD = 1      # 카드
    BANK = 2      # 계좌이체
    POINT = 3     # 포인트
    SOCIAL =4     # 소셜


class Pay(db.Model):
    __tablename__ = "pay"

    # 결제DB
    pay_id = db.Column(db.Integer, primary_key=True, autoincrement=True)# 결제 일련번호
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)# 유저 일련번호 (FK -> user.user_id)
    pay_is_pay = db.Column(db.Boolean, nullable=False, default=False)# 결제 여부 (이후 결제 1이면 완료)
    pay_money = db.Column(db.Integer, nullable=False, default=0)# 결제 금액
    pay_choice = db.Column(db.Integer,nullable=False,default=PayMethod.CARD.value) # 결제 방법: DB에는 숫자,코드에서는 Enum
    pay_date = db.Column(db.DateTime,nullable=False,default=lambda: datetime.now(timezone.utc))# 결제 날짜

    # 관계: Pay → User (N:1)
    user = db.relationship("User",backref=db.backref("payments", lazy=True),lazy=True)

    def __repr__(self):
        return f"<Pay {self.pay_id} user={self.user_id} money={self.pay_money}>"

    def to_dict(self):
        return {
            "pay_id": self.pay_id,
            "user_id": self.user_id,
            "pay_is_pay": self.pay_is_pay,
            "pay_money": self.pay_money,
            "pay_choice": self.pay_choice,
            "pay_date": self.pay_date.isoformat() if self.pay_date else None,
        }


class BasicAI(db.Model):
    __tablename__ = "basic_ai"

    # 기본AI DB
    ai_id = db.Column(db.Integer, primary_key=True, autoincrement=True)        # AI 일련번호
    ai_name = db.Column(db.String(50), unique=True, nullable=False)            # AI 이름
    ai_type = db.Column(db.Boolean, nullable=False, default=False)             # AI 유형(기본/커스텀 여부)
    ai_tip = db.Column(db.String(255), nullable=True)                          # AI 간단소개
    ai_content = db.Column(db.String(500), nullable=True)                      # AI 자세한 소개
    ai_hashtag = db.Column(db.Text, nullable=True)                             # 해시태그 리스트
    ai_price = db.Column(db.Integer, nullable=False, default=0)                # AI 가격
    ai_image = db.Column(db.String(500), nullable=True)                        # AI 이미지 경로
    ai_prompt = db.Column(db.Text, nullable=True)                              # 시스템 프롬프트
    ai_use_count = db.Column(db.Integer, nullable=False, default=0)            # AI 사용 횟수

    def __repr__(self):
        return f"<BasicAI {self.ai_id} {self.ai_name}>"

    def to_dict(self):
        return {
            "ai_id": self.ai_id,
            "ai_name": self.ai_name,
            "ai_type": self.ai_type,
            "ai_tip": self.ai_tip,
            "ai_content": self.ai_content,
            "ai_hashtag": self.ai_hashtag,
            "ai_price": self.ai_price,
            "ai_image": self.ai_image,
            "ai_prompt": self.ai_prompt,
            "ai_use_count": self.ai_use_count,
        }

class CustomAI(db.Model):
    __tablename__ = "custom_ai"

    # 커스텀 AI DB
    custom_id = db.Column(db.Integer, primary_key=True, autoincrement=True)      # 커스텀 일련번호
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)   # 유저 FK
    ai_id = db.Column(db.Integer, db.ForeignKey("basic_ai.ai_id"), nullable=False,unique=True)   # BasicAI FK(베이스 모델)
    custom_date = db.Column(db.DateTime, nullable=False,default=lambda: datetime.now(timezone.utc))  # 생성일
    custom_sell = db.Column(db.Boolean, nullable=False, default=False)           # 판매 여부 0이면 판매x 1이면 판매
    custom_sell_count = db.Column(db.Integer, nullable=False, default=0)         # 구매 횟수
    custom_delete = db.Column(db.Boolean, nullable=False, default=False)         # 삭제 여부 0이면 유지 1이면 삭제

    # 관계 CustomAI -> User N대1
    #     CustomAI -> basic 1대1
    user = db.relationship("User",backref=db.backref("custom_ais", uselist=False, lazy=True),lazy=True)
    base_ai = db.relationship("BasicAI",backref=db.backref("custom_ais", lazy=True),lazy=True)

    def __repr__(self):
        return f"<CustomAI {self.custom_id} user={self.user_id} ai={self.ai_id}>"

    def to_dict(self):
        return {
            "custom_id": self.custom_id,
            "user_id": self.user_id,
            "ai_id": self.ai_id,
            "custom_date": self.custom_date.isoformat() if self.custom_date else None,
            "custom_sell": self.custom_sell,
            "custom_sell_count": self.custom_sell_count,
            "custom_delete": self.custom_delete,
        }


class UseBox(db.Model):
    __tablename__ = "usebox"

    #유저 ai 사용기록
    use_id = db.Column(db.Integer, primary_key=True, autoincrement=True)        # 사용 일련번호
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False) # 유저 일련번호
    ai_id = db.Column(db.Integer, db.ForeignKey("basic_ai.ai_id"), nullable=False) #ai 일련번호
    use_start = db.Column(db.DateTime,nullable=False,default=lambda: datetime.now(timezone.utc))    #유저 사용시작날짜                                                                        # 사용 시작일
    use_end = db.Column(db.DateTime, nullable=True)                             # 사용 종료일

    # 관계 UseBox -> User N대1
    #     UseBox -> ai N대1
    user = db.relationship("User",backref=db.backref("useboxes", lazy=True),lazy=True)
    ai = db.relationship("BasicAI",backref=db.backref("useboxes", lazy=True),lazy=True)
    chat_logs = db.relationship("ChatLog", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UseBox {self.use_id} user={self.user_id} ai={self.ai_id}>"

    def to_dict(self):
        return {
            "use_id": self.use_id,
            "user_id": self.user_id,
            "ai_id": self.ai_id,
            "use_start": self.use_start.isoformat() if self.use_start else None,
            "use_end": self.use_end.isoformat() if self.use_end else None,
        }


class Review(db.Model):
    __tablename__ = "review"

    #ai사용 리뷰 DB
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)      # 리뷰 일련번호
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False) # 유저 일련번호
    ai_id = db.Column(db.Integer, db.ForeignKey("basic_ai.ai_id"), nullable=False) # ai일련번호
    review_write = db.Column(db.String(255), nullable=False)                    # 리뷰 작성 내용
    review_good = db.Column(db.Integer, nullable=False, default=0)              # 좋아요 수 등
    review_new = db.Column(db.DateTime,nullable=False,default=lambda: datetime.now(timezone.utc))     #리뷰 첫작성날짜                                                                      # 작성 시간
    review_modify = db.Column(db.DateTime, nullable=True)                       # 수정 시간
    review_delete = db.Column(db.Boolean, nullable=False, default=False)        # 삭제 여부

    __table_args__ = (db.UniqueConstraint("user_id", "ai_id", name="uq_user_ai_review"),) #하나의 유저가 하나의 ai에 하나씩만 쓰도록 제약걸기

    # 관계 Review -> User 1대1
    #     Review -> ai 1대1
    user = db.relationship("User",backref=db.backref("reviews", lazy=True),lazy=True)
    ai = db.relationship("BasicAI",backref=db.backref("reviews", lazy=True),lazy=True)

    def __repr__(self):
        return f"<Review {self.review_id} user={self.user_id} ai={self.ai_id}>"

    def to_dict(self):
        return {
            "review_id": self.review_id,
            "user_id": self.user_id,
            "ai_id": self.ai_id,
            "review_write": self.review_write,
            "review_good": self.review_good,
            "review_new": self.review_new.isoformat() if self.review_new else None,
            "review_modify": self.review_modify.isoformat() if self.review_modify else None,
            "review_delete": self.review_delete,
        }

class Notice(db.Model):
    __tablename__ = "notice"

    # 게시판DB
    notice_id = db.Column(db.Integer, primary_key=True, autoincrement=True)          # 게시판 일련번호
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)   # 작성자
    notice_title = db.Column(db.String(200), nullable=False)                         # 제목
    notice_write = db.Column(db.String(255), nullable=False)                         # 내용
    notice_image = db.Column(db.String(500), nullable=True)                          # 이미지 경로
    notice_view_count = db.Column(db.Integer, nullable=False, default=0)             # 조회수
    notice_like = db.Column(db.Integer, nullable=False, default=0)                   # 좋아요 수
    notice_new = db.Column(db.DateTime,nullable=False,default=lambda: datetime.now(timezone.utc)) #첫생성일자
    notice_modify = db.Column( db.DateTime,nullable=True)   #수정날짜
    notice_delete = db.Column(db.Boolean, nullable=False, default=False)             # 삭제 여부(0 등록, 1 삭제)

    # 관계: notice → User (N:1)
    user = db.relationship("User",backref=db.backref("notices", lazy=True),lazy=True)

    def __repr__(self):
        return f"<Notice {self.notice_id} title={self.notice_title}>"

    def to_dict(self):
        return {
            "notice_id": self.notice_id,
            "user_id": self.user_id,
            "notice_title": self.notice_title,
            "notice_write": self.notice_write,
            "notice_image": self.notice_image,
            "notice_view_count": self.notice_view_count,
            "notice_like": self.notice_like,
            "notice_new": self.notice_new.isoformat() if self.notice_new else None,
            "notice_modify": self.notice_modify.isoformat() if self.notice_modify else None,
            "notice_delete": self.notice_delete,
        }

class Comment(db.Model):
    __tablename__ = "comment"

    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)          # 댓글 일련번호
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)    # 댓글 작성자
    notice_id = db.Column(db.Integer, db.ForeignKey("notice.notice_id"), nullable=False)  # 어느 공지의 댓글인지
    comment_write = db.Column(db.String(255), nullable=False)                         # 댓글 내용
    comment_new = db.Column(db.DateTime,nullable=False,default=lambda: datetime.now(timezone.utc))
    comment_delete = db.Column(db.Boolean, nullable=False, default=False)             # 삭제 여부(0 등록, 1 삭제)

    user = db.relationship("User",backref=db.backref("comments", lazy=True),lazy=True)
    notice = db.relationship("Notice", backref=db.backref("comments", lazy=True), lazy=True)

    def __repr__(self):
        return f"<Comment {self.comment_id} notice={self.notice_id} user={self.user_id}>"

    def to_dict(self):
        return {
            "comment_id": self.comment_id,
            "user_id": self.user_id,
            "notice_id": self.notice_id,
            "comment_write": self.comment_write,
            "comment_new": self.comment_new.isoformat() if self.comment_new else None,
            "comment_delete": self.comment_delete,
        }

class ChatLog(db.Model):
    __tablename__ = 'chat_log'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # 대화 일련번호
    usebox_id = db.Column(db.Integer, db.ForeignKey("usebox.use_id"), nullable=False)
    question = db.Column(db.Text, nullable=False)                   # 사용자 질문
    answer = db.Column(db.Text, nullable=False)                     # AI 답변
    sql_id = db.Column(db.Integer)                                  # 하이브리드 동기화용 ID
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)) # 생성 시간

    # 관계: ChatLog → UseBox (N:1)
    # usebox = db.relationship("UseBox", backref=db.backref("chat_logs", lazy=True))

    def __repr__(self):
        return f"<ChatLog {self.id} usebox={self.usebox_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "usebox_id": self.usebox_id,
            "question": self.question,
            "answer": self.answer,
            "sql_id": self.sql_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "ai_id": self.usebox.ai_id if self.usebox else None,
            "user_id": self.usebox.user_id if self.usebox else None,
        }