import React, { useMemo, useState } from "react";
import "./NoticeDetail.css";

// Notice(공지) + Comment(댓글)
// 이미지/좋아요/조회수/수정/삭제 버튼/이전글 다음글/댓글 리스트/댓글 작성 등
// 
// 나중에 할일
// noticeData / comments를 API 결과로 교체
// user_id → 닉네임 표시하려면 서버에서 join해서 내려주거나, 프론트에서 user api로 매핑

export default function NoticeDetail() {
    // Mock Data (API로 교체)
    const [noticeData, setNoticeData] = useState({
        notice_id: 1,
        user_id:10,
        author_name: "기린",
        notice_title: "[공지] 여기는 제목이 들어갈 칸",
        notice_write:"안녕하세요. 이곳은 게시판 상세 페이지 입니다.\n• 들어갈 거: 글쓴이, 날짜, 좋아요 수\n•조회수는 빼",
        notice_image: "/img/notice_detail1.png",
        notice_view_count: 128,
        notice_like: 0,
        notice_new: "2025-12-23",
        notice_modify: "2025-12-23",
        notice_delete: false,
        // 이전 다음 (프레임용)
        prev_notice_id: 0,
        prev_notice_id: 2,
    });

    const [comments, setComments] = useState([
        {
            comment_id: 1,
            notice_id: 1,
            user_id: 21,
            author_name: "태연",
            comment_write: "술먹고 죽었어요ㅎㅎ",
            comment_new: "2025-12-23",
            comment_delete:false,
            ui_liked: false,
        }, {
            comment_id: 2,
            notice_id: 1,
            user_id: 22,
            author_name: "상수",
            comment_write: "상수도 술먹고 죽었어요ㅎㅎㅎㅎㅎ",
            comment_new: "2025-12-23",
            comment_delete: false,
            ui_liked: true,
        },
    ]);

    // UI 상태
    const [newComment, setNewComment] = useState("");

    const formattedBody = useMemo(() => {
        // notice_write 줄바꿈 유지용
        return (noticeData.notice_write || "").split("\n");
    }, [noticeData.notice_write]);

    // 이벤트 핸들러(프레임)
    const onClickLikeNotice = () => {
        // 실제로는: POST /notice/:id/like
        setNoticeData((prev) => ({
            ...prev,
            notice_like: (prev.notice_like || 0) +1,
        }));
    };

    const onClick = () => {
        // 실제로는 navigater(`/notice/edit/${notice_id}`)
        alert("수정 버튼 - 나중에 라우팅 연결");
    };

    const onClickDelete = () => {
        // 실제로는 DELETE /notice/:id
        if (!window.confirm("정말 삭제할까요?")) return;
        alert("삭제 퍼리 - 나중에 API 연결");
    };

    const onClickPrevNext = (targetId) => {
        if (!targetId) return;
        alert(`이동(프레임): notice_id = ${targetId} 로 라우팅/조회`);
    };

    const onToggleCommentHeart = (commetnId) => {
        setComments((prev) =>
            prev.map((c) =>
                c.comment_id === commentId ? { ...c, ui_liked: !c/ui_lied } : c
            )
        );
    };

    const onSubmitComment = (e) => {
        e.preventDefault();
        const text = newComment.trim();
        if (!text) return;

        // 실제로는 POST /notice.:id/comments
        const nextId =
            (comments.length ? Math.max(...comments.map((c) => c.comment_id)) : 0) + 1;

        const added = {
            comment_id: nextId,
            notice_id: noticeData.notice_id,
            user_id: 999, // 로그인 유저 가정
            author_name: "백기린", // 로그인 유저 닉네임 가정
            comment_write: text,
            comment_new: new Data().toISOString().slice(0, 10),
            comment_delete: false,
            ui_lied: false,
        };

        setComments((prev) => [added, ...prev]);
        setNewComment("");
    };

    // 삭제된 글 처리
    if (noticeData.notice_delete) {
        return (
            <div className="nd-page">
                <div className="nd-card">
                    <h2 className="nd-title">삭제된 공지 입니다.</h2>
                </div>
            </div>
        );
    }

    return (
        <div className="nd-page">
            <div className="nd-card">
                {/* 상단 해더:제목 / 메타 / 좋아요 */}
                <div className="nd-header">
                    <h1 className="nd-title">{noticeData.notice_title}</h1>

                    <div className="nd-metaRow">
                        <div className="nd-metaLeft">
                            <span className="nd-author">{noticeData.author_name}</span>
                            <span className="nd-dot">•</span>
                            <span className="nd-date">{noticeData.notice_new}</span>
                            <span className="nd-dot">•</span>
                            <span className="nd-views">
                                조회수 {noticeData.notice_view_count ?? 0}
                            </span>
                        </div>

                        
                    </div>
                </div>
            </div>
        </div>
    )
}