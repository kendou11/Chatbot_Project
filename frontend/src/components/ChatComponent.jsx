import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

const ChatComponent = () => {
    const { type } = useParams();
    const [msg, setMsg] = useState('');
    const [chat, setChat] = useState([]);
    const [intro, setIntro] = useState('');
    const [report, setReport] = useState('');
    const [loading, setLoading] = useState(false);
    const [isTyping, setIsTyping] = useState(false); // AI 답변 중 상태 추가

    const chatEndRef = useRef(null);

    const botConfigs = {
        wellness: { title: '🌿 웰니스 코치', color: '#4CAF50', placeholder: '마음 상태를 들려주세요...' },
        career: { title: '🚀 커리어 멘토', color: '#FF8C00', placeholder: '진로 고민을 입력하세요...' },
        finance: { title: '💰 금융 가이드', color: '#1E88E5', placeholder: '자산 관리 고민을 입력하세요...' },
        health: { title: '🏥 건강 매니저', color: '#E53935', placeholder: '건강 상태를 알려주세요...' },
        daily: { title: '📅 데일리 도우미', color: '#9C27B0', placeholder: '오늘 하루는 어땠나요?' },
        learning: { title: '✍️ 학습 서포터', color: '#795548', placeholder: '공부 계획을 세워볼까요?' },
        legal: { title: '⚖️ 법률 자문', color: '#607D8B', placeholder: '상담이 필요한 법률 문제를 입력하세요...' },
        tech: { title: '💻 테크 가이드', color: '#263238', placeholder: '기술적 궁금증을 해결해드릴게요.' }
    };

    const currentBot = botConfigs[type] || { title: '🤖 AI 어시스턴트', color: '#333', placeholder: '메시지를 입력하세요...' };

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [chat, isTyping]);

    useEffect(() => {
        setChat([]);
        setReport('');
        setIntro(''); // 카테고리 변경 시 이전 인트로 초기화
        const fetchIntro = async () => {
            try {
                const res = await fetch(`http://localhost:5000/api/${type}/`, { credentials: 'include' });
                const data = await res.json();
                if (data.status === "success") {
                    setIntro(data.intro_html);
                }
            } catch (err) {
                console.error(`${type} 로드 실패:`, err);
            }
        };
        fetchIntro();
    }, [type]);

    const send = async () => {
        if (!msg.trim() || isTyping) return;

        const currentMsg = msg;
        setChat(prev => [...prev, { role: 'user', text: currentMsg }]);
        setMsg('');
        setIsTyping(true); // AI 답변 시작

        try {
            const res = await fetch(`http://localhost:3000/${type}/ask`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: currentMsg }),
                credentials: 'include'
            });
            const data = await res.json();

            if (data.status === "success" || data.response) {
                setChat(prev => [...prev, { role: 'ai', text: data.response }]);
            } else {
                setChat(prev => [...prev, { role: 'ai', text: "⚠️ 답변을 가져오지 못했습니다. 로그인을 확인해주세요." }]);
            }
        } catch (error) {
            setChat(prev => [...prev, { role: 'ai', text: "⚠️ 서버와 연결이 끊어졌습니다. 잠시 후 다시 시도해주세요." }]);
        } finally {
            setIsTyping(false); // AI 답변 종료
        }
    };

    const generateReport = async () => {
        if (chat.length < 2) {
            alert("상담 내역이 부족합니다. 질문을 먼저 진행해주세요.");
            return;
        }
        setLoading(true);
        try {
            const res = await fetch(`http://localhost:3000/${type}/report`, {
                method: 'GET',
                credentials: 'include'
            });
            const data = await res.json();
            if (data.report) {
                setReport(data.report);
            } else {
                alert(data.error || "분석할 데이터가 없습니다.");
            }
        } catch (error) {
            alert("리포트 생성 중 오류가 발생했습니다.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '850px', margin: '0 auto', fontFamily: 'Pretendard, sans-serif' }}>
            <h2 style={{ textAlign: 'center', color: currentBot.color, marginBottom: '30px' }}>{currentBot.title}</h2>

            {intro && (
                <div style={{ backgroundColor: '#f9f9f9', padding: '20px', borderRadius: '12px', border: '1px solid #eee', marginBottom: '20px', fontSize: '0.95rem', color: '#444' }}
                     dangerouslySetInnerHTML={{ __html: intro }} />
            )}

            <div style={{ border: '1px solid #ddd', borderRadius: '15px', height: '500px', overflowY: 'auto', padding: '20px', backgroundColor: '#fff', marginBottom: '20px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
                {chat.length === 0 ? (
                    <div style={{ margin: 'auto', textAlign: 'center', color: '#bbb' }}>
                        <p style={{ fontSize: '1.2rem' }}>💬</p>
                        <p>무엇을 도와드릴까요? 편하게 말씀해 주세요.</p>
                    </div>
                ) : (
                    chat.map((c, i) => (
                        <div key={i} style={{ textAlign: c.role === 'user' ? 'right' : 'left' }}>
                            <div style={{
                                display: 'inline-block',
                                padding: '12px 18px',
                                borderRadius: '18px',
                                backgroundColor: c.role === 'user' ? currentBot.color : '#f1f3f5',
                                color: c.role === 'user' ? '#fff' : '#212529',
                                maxWidth: '85%',
                                textAlign: 'left',
                                boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                            }}>
                                {/* AI 답변은 마크다운으로 렌더링 */}
                                {c.role === 'ai' ? <ReactMarkdown>{c.text}</ReactMarkdown> : c.text}
                            </div>
                        </div>
                    ))
                )}
                {isTyping && (
                    <div style={{ textAlign: 'left' }}>
                        <div style={{ display: 'inline-block', padding: '10px 15px', borderRadius: '15px', backgroundColor: '#f1f3f5', color: '#888', fontSize: '0.9rem' }}>
                            답변을 생각 중입니다...
                        </div>
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>

            <div style={{ display: 'flex', gap: '10px', marginBottom: '40px' }}>
                <input style={{ flex: 1, padding: '14px', borderRadius: '10px', border: '1px solid #ddd', outline: 'none', transition: 'border 0.2s' }}
                       value={msg}
                       onChange={e => setMsg(e.target.value)}
                       onKeyPress={(e) => e.key === 'Enter' && send()}
                       placeholder={currentBot.placeholder}
                       disabled={isTyping} />
                <button onClick={send}
                        disabled={isTyping}
                        style={{ padding: '0 30px', backgroundColor: isTyping ? '#ccc' : currentBot.color, color: '#fff', border: 'none', borderRadius: '10px', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.2s' }}>
                    전송
                </button>
            </div>

            <div style={{ borderTop: '2px solid #f8f9fa', paddingTop: '30px', paddingBottom: '80px' }}>
                <button onClick={generateReport} disabled={loading || chat.length < 2}
                        style={{ width: '100%', padding: '16px', backgroundColor: '#212529', color: '#fff', border: 'none', borderRadius: '12px', cursor: (loading || chat.length < 2) ? 'default' : 'pointer', fontSize: '1.1rem', fontWeight: '600' }}>
                    {loading ? "📊 분석 보고서 생성 중..." : `📊 ${currentBot.title} AI 리포트 생성`}
                </button>
                {report && (
                    <div style={{ marginTop: '25px', padding: '30px', backgroundColor: '#fff', borderRadius: '20px', border: '1px solid #e9ecef', boxShadow: '0 10px 30px rgba(0,0,0,0.08)', lineHeight: '1.8' }}>
                        <h3 style={{ borderBottom: '2px solid #f1f3f5', paddingBottom: '10px', marginBottom: '20px' }}>상담 분석 리포트</h3>
                        <ReactMarkdown>{report}</ReactMarkdown>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatComponent;