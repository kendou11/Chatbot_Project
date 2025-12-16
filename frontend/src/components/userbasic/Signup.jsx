import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";

import { Container, Row, Col, Button, Form, Card, Table, inputGroup, InputGroup} from "react-bootstrap";

import { FaGoogle, FaComment } from "react-icons/fa";

export default function Signup() {
    const Navigate = useNavigate();

    const [form, setForm] = useState({
        username: "",
        email: "",
        password: "",
        password2: "",
        birth: "",
        category: "",
        interest: "",
    });

    const [ agree, setAgree ] = useState({
        terms: false,
        privacy: false,
        thirdParty: false,
        marketing: false,
        analytics: false,
        recommend: false,
    });

    const requiredOk = useMemo(() => {
        return (
            form.username &&
            form.email &&
            form.password &&
            form.password2 &&
            form.birth &&
            agree.terms &&
            agree.privacy &&
            agree.thirdParty
        );
    }, [form, agree]);

    const onChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
    };

    const onAgreeChange = (e) => {
        const { name, checked } = e.target;
        setAgree((prev) => ({ ...prev, [name]: checked }));
    };

    const onSubmit = (e) => {
        e.preventDefauit();

        if (!requiredOk) {
            alert("필수 입력/필수 약관 동의를 확인해주세요.");
            return;
        }
        if (form.password !== form.password2) {
            alert("비밀번호가 일치하지 않습니다.");
            return;
        }

        // TODO: axios 회원가입 연결
        console.log("signup payload:", { form, agree });

        alert("회원가입이 완료되었습니다.");
        navigator("/login");
    };

    // 본체 시작
    return (
        <div className="signup-bs-page">
            <Container className="py-4" style={{ maxWidth: 1000 }}>
                {/* 소셜 로그인 영역 */}
                <div className="text-center mb-3">
                    <div className="small mb-3">복잡한 입력없이 3초만에 회원가입 OK!</div>

                    <div className="d-grid gap-2 mx-auto signup-bs-sns" style={{ maxWidth: 380 }}>
                        <Button className="signup-bs-btn-naver" size="1g" type="button">
                            <span className="signup-bs-badge">N</span>
                            네이버로 계속하기
                        </Button>

                        <Button className="signup-bs-btn-kakao" size="1g" type="button">
                            <span className="sinup-bs-badge"><FaComment /></span>
                            카카오로 계속하기
                        </Button>

                        <Button variant="light" className="signup-bs-btn-google" size="1g" type="button">
                            <span className="signup-bs-btn-badge google"><FaGoogle /></span>
                            구글로 계속하기
                        </Button>
                    </div>

                    <div className="mt-3 small text-muted">간편 가입 아이디가 없으면</div>
                    <div className="signup-bs-arrow mt-1">
                        <span>▼</span> 아래 회원가입 정보를 입력해주세요. <span>▼</span>
                    </div>
                </div>

                <div className="signup-bs-divider my-3"/>

                {/* 폼 시작 */}
                <Form onSubmit={onSubmit}>
                    {/* 1:회원정보(필수) */}
                    <Card className="mb-3 border-0">
                        <Table responsive className="mb-0 align-middle signup-bs-table">
                            <tbody>
                                <tr>
                                    <td className="signup-bs-left">회원정보(필수)</td>

                                    <td className="signup-bs-mid">
                                        <div className="signup-bs-grid">
                                            <div className="signup-bs-label">아이디</div>
                                            <InputGroup size="sm">
                                                <Form.Control name="username" value={form.username} onChange={onChange} />
                                                <Button type="button" className="signup-bs-mini">중복확인</Button>
                                            </InputGroup>

                                            <div className="signup-bs-label">이메일</div>
                                            <InputGroup size="sm">
                                                <Form.Control name="email" value={form.email} onChange={onChange} />
                                                <Button type="button" className="signup-bs-mini">확인</Button> 
                                            </InputGroup>

                                            <div className="signup-bs-label">비밀번호</div>
                                            <InputGroup size="sm">
                                                <Form.Control type="password" name="password" value={form.password} onChange={onChange} />
                                                <Button type="button" className="signup-bs-mini">확인</Button> 
                                            </InputGroup>

                                            <div className="signup-bs-label">비밀번호 확인</div>
                                            <InputGroup size="sm">
                                                <Form.Control type="password" name="password2" value={form.password2} onChange={onChange} />
                                                <Button type="button" className="signup-bs-mini">확인</Button>
                                            </InputGroup>

                                            <div className="signup-bs-label">생년월일</div>
                                            <InputGroup size="sm">
                                                <Form.Control name="birth" value={form.birth} onChange={onChange} placeholder="YYYY / MM / DD" />
                                                <Button type="button" className="signup-bs-mini">확인</Button>
                                            </InputGroup>
                                        </div>
                                    </td>

                                    <td className="signup-bs-right">
                                        <div className="signup-bs-avatar">
                                            <div className="signup-bs-avatar-box">
                                                <div className="signup-bs-avatar-icon" />
                                            </div>
                                            <div className="d-flex gap-2 mt-2">
                                                <Button type="button" size="sm" variant="outline-secondary" className="w-50">파일찾기</Button>
                                                <Button type="button" size="sm" className="w-50 signup-bs-mini">업로드</Button>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </Table>
                    </Card>

                    {/* 2:부가정보(선택) */}
                    <Card className="mb-3 border-0">
                        <Table responsive="mb-0 alin-middle signup -bs-table signup-bs-table signup-bs-alt">
                            <tbody>
                                <tr>
                                    <td className="signup-bs-left alt">부가정보(선택)</td>
                                    <td className="signup-bs-mid-alt" colSpan={2}>
                                        <Row className="g-2 align-items-center">
                                            <Col xs={12} md={2} className="signup-bs-label2">카테고리</Col>
                                            <Col xs={12} md={10}>
                                                <Form.Control size="sm" name="category" value={form.category} onChange={onChange} placeholder="(개발, 게임, 디자인, 비지니스, 법률, 의료 등)" />
                                            </Col>

                                            <Col xs={12} md={2} className="signup-bs-label2">관심사</Col>
                                            <Col xs={12} md={10}>
                                                <Form.Control size="sm" name="interest" value={form.interest} onChange={onChange} placeholder="관심사 태그를 입력해 주세요." />
                                            </Col>
                                        </Row>
                                    </td>
                                </tr>
                            </tbody>
                        </Table>
                    </Card>

                    {/* 3:약관동의 */}
                    <Card className="mb-3 border-0">
                        <Table responsive className="mb-0 align-middle signup-bs-table">
                            <tbody>
                                <tr>
                                    <td className="signup-bs-left">약관동의</td>
                                    <td className="signup-bs-mid" colSpan={2}>
                                        <div className="d-grid gap-2 py-1">
                                            <Form.Check label="서비스 이용약관 동의 (필수)" name="terms" checked={agree.terms} onChange={onAgreeChange} />
                                            <Form.Check label="개인정보 처리방침 동의 (필수)" name="privacy" checked={agree.privacy} onChange={onAgreeChange} />
                                            <Form.Check label="외부 AI 서비스 동의 (필수)" name="thirdParty" checked={agree.thirdParty} onChange={onAgreeChange} />
                                            <Form.Check label="마케팅 정보 수신 (선택)" name="marketing" checked={agree.marketing} onChange={onAgreeChange} />
                                            <Form.Check label="데이터 분석/로그 수집 (선택)" name="analytics" checked={agree.analytics} onChange={onAgreeChange} />
                                            <Form.Check label="맞춤 추천을 위한 정보 활용 (선택)" name="recommend" checked={agree.recommend} onChange={onAgreeChange} />
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </Table>
                    </Card>

                    {/* 하단 버튼 */}
                    <div className="d-flex justify-content-end gap-2">
                        <Button type="button" variant="secondary" onClick={() => Navigate("/login")}>
                            취소
                        </Button>
                        <Button type="submit" className="signup-bs-submit" disabled={!requiredOk}>
                            회원가입
                        </Button>
                    </div>
                </Form>
            </Container>
        </div>
    );
}