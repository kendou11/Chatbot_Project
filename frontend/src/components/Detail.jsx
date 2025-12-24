// import { useMemo, useState } from "react";
import "./Detail.css";

export default function Detail() {
    // public/img 안에 사진 넣기
    const review = [{
        id: 1,
        name: "카피바라",
        text: "저는 돈이 부족해여! 고치만 야무지게 먹을거다!!",
        avatar: "/img/detail-1.png",
    },
    {
        id: 2,
        name: "수도승",
        text: "나는 오늘 안간다 후후...20일만 지나면 야무지게 먹어주지\nㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ",
        avatar: "/img/detail-1.png",
    },
    {
        id: 3,
        name: "기린",
        text: "응애 나 애기 기린",
        avatar: "/img/detail-1.png",
    },
    {
        id: 4,
        name: "예노",
        text: "집에 가고싶다.",
        avatar: "/img/detail-1.png",
    },
    ];
    return (
        <main className="wf">
            <div className="wf-wrap">
                {/* 상단 */}
                <section className="wf-top">
                    <div className="wf-leftIcon">
                        <img className="wf-logo" src="/img/detail-2.png" alt="AI 로고" />
                    </div>

                    <div className="wf-rightText">
                        <h1 className="wf-title">베이직/개인비서 이름란.</h1>
                        <p className="wf-desc">
                            전문 분야에 맞춰 생성되는 직무 맞춤형 AI 비서입니다.
                            선택한 직무의 지식업무 흐름에 학습해 당신의 목표에 맞는 실전형 지원을 제공합니다.<br />
                            예시로 써논거임.
                        </p>
                        <p className="wf-tags">
                            #직무맞춤AI비서 #개인비서 #전문분야특화
                        </p>
                    </div>
                </section>

                <div className="wf-line" />

                {/* 리뷰 */}
                <section className="wf-reviews">
                    <span className="wf-label">Reviews</span>

                    <div className="wf-list">
                        {review.map((r) => (
                            <div className="wf-row" key={r.id}>
                                {/* 프로필 */}
                                <div className="wf-avatarBox">
                                    <img className="wf-avatarImg" src={r.avatar} alt={`${r.name} 아바타`} />
                                </div>
                                {/* 이름 + 리뷰 텍스트 */}
                                <div className="wf-reviewText">
                                    <div className="wf-name">{r.name}</div>
                                    <div className="wf-comment">{r.text}</div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* 리뷰 작성 */}
                    <div className="review-box"></div>
                    
                    <div className="wf-row">
                        <form className="review-form">
                            <textarea className="review-textarea" placeholder="리뷰를 입력하세요"/>
                            <button className="review-btn"> 등록하기 </button>
                        </form>
                    </div>

                </section>

                {/* 하단 */}
                <section className="wf-bottom">
                    <div className="wf-wrap">
                        <button className="wf-cta" type="button">
                            대화 시작하기
                        </button>
                    </div>
                </section>
            </div>
        </main>
    )
}