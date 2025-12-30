import { useState, useEffect } from "react";
import { useNavigate, useParams } from 'react-router-dom';
import "./Detail.css";
import * as Api from '../api/AI_Detail_Api.js';

export default function Detail() {  // props로 aiId 받기
    const { aiId } = useParams();
    console.log('🔍 useParams aiId:', aiId);
    const [aiData, setAiData] = useState(null);
    const [reviews, setReviews] = useState([]);
    const [newReview, setNewReview] = useState('');
    const [canWrite, setCanWrite] = useState(false);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchDetail();
    }, [aiId]);

    const fetchDetail = async () => {
        try {
            const data = await Api.fetchAiDetail(aiId);
            console.log('📦 API 응답:', data);
            setAiData(data.ai);
            setReviews(data.reviews);
            setCanWrite(data.can_write_review);
            setLoading(false);
        } catch (error) {
            console.error('AI 정보 로드 실패:', error);
            setLoading(false);
        }
    };

    const handleSubmitReview = async (e) => {
        e.preventDefault();
        if (!newReview.trim() || !canWrite) return;

        try {
            const newReviewData = await Api.createReview(aiId, newReview);
            setReviews([newReviewData, ...reviews]);
            setNewReview('');
            setCanWrite(false);
        } catch (error) {
            alert(error.message);
        }
    };

    if (loading) return <div>로딩 중...</div>;
    if (!aiData) return <div>AI를 찾을 수 없습니다.</div>;

    return (
        <main className="wf">
            <div className="wf-wrap">
                <section className="wf-top">
                    <div className="wf-leftIcon">
                        <img className="wf-logo" src={aiData.ai_image || "/img/detail-2.png"} alt="AI 로고" />
                    </div>
                    <div className="wf-rightText">
                        <h1 className="wf-title">{aiData.ai_name}</h1>
                        <p className="wf-desc">{aiData.ai_content}</p>
                        <p className="wf-tags">{aiData.ai_hashtag}</p>
                    </div>
                </section>

                <div className="wf-line" />

                <section className="wf-reviews">
                    <span className="wf-label">Reviews ({reviews.length})</span>
                    
                    <div className="wf-list">
                        {reviews.map((r) => (
                            <div className="wf-row" key={r.review_id}>
                                <div className="wf-avatarBox">
                                    <img className="wf-avatarImg" src="/img/detail-1.png" alt="아바타" />
                                </div>
                                <div className="wf-reviewText">
                                    <div className="wf-name">사용자{r.user_id}</div>
                                    <div className="wf-comment">{r.review_write}</div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {canWrite && (
                        <form className="review-form" onSubmit={handleSubmitReview}>
                            <textarea 
                                className="review-textarea" 
                                placeholder="리뷰를 입력하세요"
                                value={newReview}
                                onChange={(e) => setNewReview(e.target.value)}
                                maxLength={255}
                            />
                            <button className="review-btn" type="submit">등록하기</button>
                        </form>
                    )}
                    {!canWrite && (
                        <div className="review-box">
                            {localStorage.getItem('access_token') 
                                ? '이미 리뷰를 작성하셨거나 AI를 사용하지 않으셨습니다.' 
                                : '리뷰 작성은 로그인 후 AI 사용 시 가능합니다.'
                            }
                        </div>
                    )}
                </section>

                <section className="wf-bottom">
                    <div className="wf-wrap">
                        <button className="wf-cta" type="button" onClick={() => navigate(`/${aiData.ai_content}`)}>
                            대화 시작하기 (₩{aiData.ai_price})
                        </button>
                    </div>
                </section>
            </div>
        </main>
    );
}
