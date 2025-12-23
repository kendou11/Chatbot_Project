import React, { useEffect, useState, useMemo, useRef } from "react";
import { MainSummary } from "../api/Main_Api";
import { Container, Row, Col, Image } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

const AIIntroduce = () => {
    const [noticeData, setNoticeData] = useState([]);
    const [Loading, setLoading] = useState(true);
    const navigate = useNavigate();

    // StrictMode에서 useEffext 2번 실행 방지용
    const fetchedRef = useRef(false);

    // 페이지네이션 상태 설정
    const [page, setPage] = useState(1);
    const pageSize = 5;   //한 페이지에 보여줄 게시글 수

    // 모바일 감지 (480ox 기준)
    const [isMobile, setIsMobile] = useState(() =>
        typeof window !== "undefined" ? window.innerWidth <= 480 : false);

    // resize 이벤트로 모바일 여부 갱신
    useEffect(() => {
        const onResize = () => setIsMobile(window.innerWidth <= 480);
        window.addEventListener("resize", onResize);
        return () => window.removeEventListener("resize", onResize);
    }, []);

    // API 데이터 불러오기
    useEffect(() => {
        if (document.body.dataset.apiLoaded === 'true') return;  //호출 2번되는거 방지하기
        document.body.dataset.apiLoaded = 'true';

        const noticeData = async () => {
            try {
                const data = await MainSummary();  //API 호출
                console.log("✅ 메인 데이터 불러오기 성공!", data);  //성공 로그 후에 삭제 가능

                if (data && data.success && Array.isArray(data.notice)) {
                    // Notice 데이터 매핑 (API 필드 → 기존 구조 맞춤)
                    const mappedNoticeData = data.notice.map((item) => ({
                        id: item.notice_id,
                        title: item.notice_title,
                        writer: item.user_nickname,
                        views: item.notice_view_count
                    }));

                    setNoticeData(mappedNoticeData);
                } else {
                    console.warn("⚠️ 데이터 성공이지만 notice 배열 없음");
                    setNoticeData([]);
                }
            } catch (error) {
                console.error("❌ 메인 데이터 불러오기 실패:", error);
                setNoticeData([]);
            } finally {
                setLoading(false);
            }
        };

        noticeData();
    }, [     ]);

    // 총 페이지 수
    const totalPages = useMemo(() => {
        return Math.max(1, Math.ceil(noticeData.length / pageSize));
    }, [noticeData.length, pageSize]);

    // 현재 페이지가 범위를 벗어나면 보정
    useEffect(() => {
        if (page > totalPages) setPage(totalPages);
        if (page < 1) setPage(1);
    }, [page, totalPages]);

    // 현재 페이지에 보여줄 데이터만 slice
    const pagedNoticeData = useMemo(() => {
        const start = (page - 1) * pageSize;
        return noticeData.slice(start, start + pageSize);
    }, [noticeData, page, pageSize]);

    // 페이지 버튼 개수 (pc 5 / 모바일 3)
    const visibleCount = isMobile ? 3 : 5;

    // 페이지 번호 범위 계산 (6페이지는 6~10 느낌)
    const { startPage, endPage } = useMemo(() => {
        let start = page - Math.floor(visibleCount / 2);
        let end = start + visibleCount - 1;

        if (start < 1) {
            start = 1;
            end = Math.min(totalPages, start + visibleCount - 1);
        }
        if (end > totalPages) {
            end = totalPages;
            start = Math.max(1, end - visibleCount + 1);
        }
        return { startPage: start, endPage: end };
    }, [page, totalPages, visibleCount]);

    // 페이지 번호 배열
    const pageNumbers = useMemo(() => {
        const arr = [];
        for (let p = startPage; p <= endPage; p++) arr.push(p);
        return arr;
    }, [startPage, endPage]);

    // 이동 함수
    const goPage = (p) => setPage(p);

    // 페이지 slice랑 분리
    const isEmpty = !Loading && noticeData.length === 0;


    return (
        <section>
            <div className="Introduce">
                <Image src='/img/main_slider_img.png' alt="웹사이트_설명" className="AI_introduce_img" fluid />
            </div>

            <div className="service_section">
                <div className="membership_img">
                    <Container className="membership_text">
                            <p>님의 <br /> 맴버십 전용 혜택!</p>
                        <Row>
                            <Col xs={6} md={4}>
                                <Image src='/img/Membership.gif' alt="멤버십_가입_소개_gif파일" className="membership_gif" roundedCircle />
                            </Col>
                        </Row>
                    </Container>
                </div>
            </div>

            <div className="AICategoty_all">
                <Container className="AiCategory_container">
                    <Row className="circle_Row">
                        <h1>Basic Category</h1>
                        <Col xs={6} md={4} className="AICategory_circle">
                            <div className="circle_div">
                                <Image src="/img/Business.png" roundedCircle />
                                <div className="circle_text d-none d-lg-block">
                                    <h2>비지니스</h2>
                                    <p>성장과 수익 구조를<br />설계합니다.</p>
                                </div>
                            </div>
                        </Col>

                        <Col xs={6} md={4} className="AICategory_circle">
                            <div className="circle_div">
                                <Image src="/img/Designer.png" roundedCircle />
                                <div className="circle_text d-none d-lg-block">
                                    <h2>디자이너</h2>
                                    <p>사용자의 경험을<br />설계합니다.</p>
                                </div>
                            </div>
                        </Col>

                        <Col xs={6} md={4} className="AICategory_circle">
                            <div className="circle_div">
                                <Image src="/img/Developer.png" roundedCircle />
                                <div className="circle_text d-none d-lg-block">
                                    <h2>개발/엔지니어</h2>
                                    <p>아이디어를 실제 서비스로<br />구현합니다.</p>
                                </div>
                            </div>
                        </Col>

                        <Col xs={6} md={4} className="AICategory_circle">
                            <div className="circle_div">
                                <Image src="/img/Legal.png" roundedCircle />
                                <div className="circle_text d-none d-lg-block">
                                    <h2>법률/재무</h2>
                                    <p>리스크를 관리하고<br />안정성을 확보합니다.</p>
                                </div>
                            </div>
                        </Col>

                        <Col xs={6} md={4} className="AICategory_circle">
                            <div className="circle_div">
                                <Image src="/img/Planner.png" roundedCircle />
                                <div className="circle_text d-none d-lg-block">
                                    <h2>기획/PM</h2>
                                    <p>제품의 방향과 완성도를<br />관리합니다.</p>
                                </div>
                            </div>
                        </Col>

                        <Col xs={6} md={4} className="AICategory_circle">
                            <div className="circle_div">
                                <Image src="/img/Medical.png" roundedCircle />
                                <div className="circle_text d-none d-lg-block">
                                    <h2>의료/서비스</h2>
                                    <p>전문적인 의료 경험을<br />제공합니다.</p>
                                </div>
                            </div>
                        </Col>
                    </Row>
                </Container>
            </div>

            <div className="membership_all">
                <Container className="membership_container">
                    <Row className="membership_Row">
                        <h1>Membership Category</h1>
                        <Col xs={6} md={3} className="membership_circle">
                            <div className="membership_circle_div">
                                <Image src="/img/membership_img.png" roundedCircle />
                            </div>
                        </Col>
                        <Col xs={6} md={3} className="membership_circle">
                            <div className="membership_circle_div">
                                <Image src="/img/membership_img.png" roundedCircle />
                            </div>
                        </Col>
                        <Col xs={6} md={3} className="membership_circle">
                            <div className="membership_circle_div">
                                <Image src="/img/membership_img.png" roundedCircle />
                            </div>
                        </Col>
                        <Col xs={6} md={3} className="membership_circle">
                            <div className="membership_circle_div">
                                <Image src="/img/membership_plus_img.png" roundedCircle />
                            </div>
                        </Col>
                    </Row>
                </Container>
            </div>

            <div className="notice">
                <div className="notice-header">
                    <h2>게시판</h2>
                    <div className="notice-actions">
                        <button className="my-board-btn" onClick={() => navigate("/NoticeMy")}>내 게시글</button>

                        <button className="write-btn" onClick={() => navigate('/NoticeWrite')}>작성</button>
                    </div>
                </div>

                <div className="notice-table">
                    <div className="notice-head">
                        <span>번호</span>
                        <span>제목</span>
                        <span>작성자</span>
                        <span>조회수</span>
                    </div>

                    {pagedNoticeData.length > 0 ? (
                        pagedNoticeData.map((item) => (
                            <div
                                className="notice-row"
                                key={item.id}
                                onClick={() => navigate(`/notice/${item.id}`)}
                            >
                                <span>{item.id}</span>
                                <span className="title">{item.title}</span>
                                <span>{item.writer}</span>
                                <span>{item.views}</span>
                            </div>
                        ))
                    ) : !Loading ? (
                        <div style={{ padding: 16, textAlign: "center" }}>
                            게시글이 없습니다.
                        </div>
                    ) : null}
                </div>

                {/* 페이지네이션 */}
                <div className="pagination_all">
                    <div className="pagination">
                        {/* ◀ */}
                        <button className="page-arrow" onClick={() => goPage(page - 1)} disabled={page === 1} aria-label="이전 페이지">◀</button>

                        {/* 숫자 버튼 */}
                        {pageNumbers.map((p) => (
                            <button key={p} className={`page-num ${page === p ? "active" : ""}`} onClick={() => goPage(p)} aria-current={page === p ? "page" : undefined}>{p}</button>
                        ))}

                        {/* ▶ */}
                        <button className="page-arrow" onClick={() => goPage(page + 1)} disabled={page === totalPages} aria-label="다음 페이지">▶</button>
                    </div>
                </div>

            </div>
        </section>
    );
};

export default AIIntroduce;