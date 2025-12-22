import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { debounce } from 'lodash';  // 실시간 중복체크 딜레이 처리 아이디 입력시 api 불려와야하는데 너무 빠르게 불러오면 비용up
import { Id_Check, New_User } from '../../api/User_Api';  // API 연동

import { Container, Row, Col, Button, Form, Card, Table, InputGroup} from "react-bootstrap";
import { FaGoogle, FaComment } from "react-icons/fa";   //부트스트랩 불러오기


//회원가입 함수 생성
export default function Signup() {
    const Navigate = useNavigate();

    //기본 폼 세팅
    const [form, setForm] = useState({
        nickname: "",
        email: "",
        password: "",
        password2: "",
        birth: "",
    });

    //필수 약관 체크 할수 있게 하기
    const [ agree, setAgree ] = useState({
        terms: false,
        privacy: false,
        thirdParty: false,
    });

    //중복체크 상태들 (핵심 기능)
    const [checking, setChecking] = useState({ nickname: false, email: false }); //초기값을 false 로두고 시작
    const [available, setAvailable] = useState({ nickname: null, email: null }); // 없다고 시작하기
    const [errors, setErrors] = useState({});

    //실시간 중복체크 함수
    const Id_Check_Api = debounce(async (type, value) => {
        if (type === 'nickname' && value.length < 2) return;
        if (type === 'email' && !value.includes('@')) return;

        setChecking(prev => ({ ...prev, [type]: true }));
        try {
            const data = await Id_Check(type, value);
            setAvailable(prev => ({ ...prev, [type]: data.available }));
            setErrors(prev => ({ ...prev, [type]: data.available ? '' : data.message }));
        } catch {
            setErrors(prev => ({ ...prev, [type]: '서버 오류' }));
        } finally {
            setChecking(prev => ({ ...prev, [type]: false }));
        }
    }, 500);




    //회원가입 버튼 활성화
    const requiredOk = useMemo(() => {
        return (
            form.nickname &&
            form.email &&
            form.password &&
            form.password2 &&
            agree.terms &&
            agree.privacy &&
            agree.thirdParty &&
            available.nickname === true &&  // 🔄 중복체크 통과 필수
            available.email === true
        );
    }, [form, agree,available]);



    //데이터 form폼에 저장해주기
    const onChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
        setErrors(prev => ({ ...prev, [name]: '' }));

        // 🔄 실시간 중복체크
        if (name === 'nickname' || name === 'email') {
            Id_Check_Api(name, value);
        }
    };

    // 생년월일 입력란 추후에 작성해도 되도록 하기
    const onBirthChange = (e) => {
        let value = e.target.value.replace(/[^0-9]/g, '').slice(0, 8);

        let newValue = '';
        if (value.length >= 8) {
            newValue = `${value.slice(0,4)} / ${value.slice(4,6)} / ${value.slice(6,8)}`;
        } else if (value.length >= 6) {
            newValue = `${value.slice(0,4)} / ${value.slice(4,6)} / `;
        } else if (value.length >= 4) {
            newValue = `${value.slice(0,4)} / `;
        } else {
            newValue = value;
        }

        setForm(prev => ({ ...prev, birth: newValue }));
        setTimeout(() => e.target.setSelectionRange(newValue.length, newValue.length), 0);
    };

    //데이터 check폼에 저장해주기
    const onAgreeChange = (e) => {
        const { name, checked } = e.target;
        setAgree((prev) => ({ ...prev, [name]: checked }));
    };



    //지금까지 만든 함수 이용해서 최종 API연동 회원가입 구현 조건
    const onSubmit = async(e) => {
        e.preventDefault();

        if (!requiredOk) {
            alert("필수 입력/필수 약관 동의를 확인해주세요.");
            return;
        }
        if (form.password !== form.password2) {
            alert("비밀번호가 일치하지 않습니다.");
            return;
        }

        try {
            const birthdateClean = form.birth
                .replace(/[^0-9]/g, '')
                .substring(0, 8)
                .replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3') || null;

            const payload = {
                nickname: form.nickname,
                email: form.email,
                password: form.password,
                birthdate: birthdateClean,  // YYYY-MM-DD 변환
            };

            const result = await New_User(payload);
            if (result.success) {
                alert("회원가입이 완료되었습니다.");
                Navigate("/login");
            }
        } catch (error) {
            alert(error.response?.data?.error || '회원가입 실패');
        }
    };

    //중복확인 버튼 클릭시 실시
    const handleCheckDuplicate = (type) => {
        if (form[type].length < 2) {
            alert('2글자 이상 입력해주세요.');
            return;
        }
        Id_Check_Api(type, form[type]);
    };

    // 본체 시작
    return (
        <div className="signup-bs-page">
            <Container className="py-4" style={{ maxWidth: 1000 }}>
                {/* 소셜 로그인 영역 */}
                <div className="text-center mb-3">
                    <div className="small mb-3">복잡한 입력없이 3초만에 회원가입 OK!</div>

                    <div className="d-grid gap-2 mx-auto signup-bs-sns" style={{ maxWidth: 380 }}>
                        <Button className="signup-bs-btn-naver" size="lg" type="button">
                            <span className="signup-bs-badge">N</span>
                            네이버로 계속하기
                        </Button>

                        <Button className="signup-bs-btn-kakao" size="lg" type="button">
                            <span className="sinup-bs-badge"><FaComment /></span>
                            카카오로 계속하기
                        </Button>

                        <Button variant="light" className="signup-bs-btn-google" size="lg" type="button">
                            <span className="signup-bs-btn-badge google"><FaGoogle /></span>
                            구글로 계속하기
                        </Button>
                    </div>

                    <div className="mt-3 small text-muted">간편 가입 아이디가 없으면</div>
                    <div className="signup-bs-arrow mt-1">
                        <span>▼</span> 아래 회원가입 정보를 입력해주세요. <span>▼</span>
                    </div>
                </div>

                <div className="signup-bs-divider my-3" />

                {/* 회원정보 시작 */}
                <Form onSubmit={onSubmit}>
                    {/* 1:회원정보(필수) */}
                    <Card className="mb-3 border-0">
                        <Table responsive className="mb-0 align-middle signup-bs-table">
                            <tbody>
                                <tr>
                                    <td className="signup-bs-left">회원정보(필수)</td>

                                    <td className="signup-bs-mid">
                                        <div className="signup-bs-grid">

                                            {/* 닉네임: 실시간+수동 중복체크 */}
                                            <div className="signup-bs-label">닉네임</div>
                                            <InputGroup size="sm">
                                                <Form.Control name="nickname" value={form.nickname} onChange={onChange}
                                                    className={errors.nickname ? 'is-invalid' : available.nickname === true ? 'is-valid' : ''}
                                                    placeholder="닉네임 입력"/>
                                            {/* 중복체크 확인시 변하는 css*/}
                                                <Button
                                                    type="button" className={`signup-bs-mini ${checking.nickname ? 'text-white bg-primary' : ''}`}
                                                    onClick={() => handleCheckDuplicate('nickname')} disabled={checking.nickname}>
                                                    {checking.nickname ? ( <span className="spinner-border spinner-border-sm" /> ) : '중복확인'}
                                                </Button>
                                            </InputGroup>
                                            {/* 에러메세지 */}
                                            {errors.nickname && <div className="form-text text-danger small mb-2">{errors.nickname}</div>}
                                            {available.nickname === true && <div className="form-text text-success small mb-2">사용가능한 닉네임입니다</div>}

                                            {/*이메일: 실시간+수동 중복체크 */}
                                            <div className="signup-bs-label">이메일(ID)</div>
                                            <InputGroup size="sm">
                                                <Form.Control name="email" type="email" value={form.email} onChange={onChange}
                                                    className={errors.email ? 'is-invalid' : available.email === true ? 'is-valid' : ''}
                                                    placeholder="example@email.com" />
                                            {/* 중복체크 확인시 변하는 css*/}
                                                <Button
                                                    type="button" className={`signup-bs-mini ${checking.email ? 'text-white bg-primary' : ''}`}
                                                    onClick={() => handleCheckDuplicate('email')} disabled={checking.email}>
                                                    {checking.email ? (<span className="spinner-border spinner-border-sm" />) : '확인'}
                                                </Button>
                                            </InputGroup>
                                            {/* 에러메세지 */}
                                            {errors.email && <div className="form-text text-danger small mb-2">{errors.email}</div>}
                                            {available.email === true && <div className="form-text text-success small mb-2">사용가능한 이메일입니다</div>}

                                            {/* 비밀번호 */}
                                            <div className="signup-bs-label">비밀번호</div>
                                            <InputGroup size="sm">
                                                <Form.Control type="password" name="password" value={form.password} onChange={onChange} placeholder="8자 이상"/>
                                                <Button type="button" className="signup-bs-mini">확인</Button> 
                                            </InputGroup>

                                            <div className="signup-bs-label">비밀번호 확인</div>
                                            <InputGroup size="sm">
                                                <Form.Control type="password" name="password2" value={form.password2} onChange={onChange}  />
                                                <Button type="button" className="signup-bs-mini">확인</Button>
                                            </InputGroup>

                                            {/* 생년월일 */}
                                            <div className="signup-bs-label">생년월일</div>
                                            <InputGroup size="sm">
                                                <Form.Control name="birth" value={form.birth} onChange={onBirthChange} placeholder="선택사항" maxLength="14"/>
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
                        <Table responsive="mb-0 alin-middle signup-bs-table signup-bs-table signup-bs-alt">
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