// import '../../css/User.css'
// import { useState, useMemo } from "react";
// import { useNavigate } from "react-router-dom";
// import { debounce } from 'lodash';  // 실시간 중복체크 딜레이 처리 아이디 입력시 api 불려와야하는데 너무 빠르게 불러오면 비용up
// import { Id_Check, New_User } from '../../api/User_Api';  // API 연동

// import { Container, Row, Col, Button, Form, Card, Table, InputGroup} from "react-bootstrap";
// import { FaGoogle, FaComment } from "react-icons/fa";   //부트스트랩 불러오기


// //회원가입 함수 생성
// export default function Signup() {
//     const Navigate = useNavigate();

//     //기본 폼 세팅
//     const [form, setForm] = useState({
//         nickname: "",
//         email: "",
//         password: "",
//         password2: "",
//         birth: "",
//     });

//     //필수 약관 체크 할수 있게 하기
//     const [ agree, setAgree ] = useState({
//         terms: false,
//         privacy: false,
//         thirdParty: false,
//     });

//     //중복체크 상태들 (핵심 기능)
//     const [checking, setChecking] = useState({ nickname: false, email: false }); //초기값을 false 로두고 시작
//     const [available, setAvailable] = useState({ nickname: null, email: null }); // 없다고 시작하기
//     const [errors, setErrors] = useState({});

//     //실시간 중복체크 함수
//     const Id_Check_Api = debounce(async (type, value) => {
//         if (type === 'nickname' && value.length < 2) return;
//         if (type === 'email' && !value.includes('@')) return;

//         setChecking(prev => ({ ...prev, [type]: true }));
//         try {
//             const data = await Id_Check(type, value);
//             setAvailable(prev => ({ ...prev, [type]: data.available }));
//             setErrors(prev => ({ ...prev, [type]: data.available ? '' : data.message }));
//         } catch {
//             setErrors(prev => ({ ...prev, [type]: '서버 오류' }));
//         } finally {
//             setChecking(prev => ({ ...prev, [type]: false }));
//         }
//     }, 500);




//     //회원가입 버튼 활성화
//     const requiredOk = useMemo(() => {
//         return (
//             form.nickname &&
//             form.email &&
//             form.password &&
//             form.password2 &&
//             agree.terms &&
//             agree.privacy &&
//             agree.thirdParty &&
//             available.nickname === true &&  // 🔄 중복체크 통과 필수
//             available.email === true
//         );
//     }, [form, agree,available]);



//     //데이터 form폼에 저장해주기
//     const onChange = (e) => {
//         const { name, value } = e.target;
//         setForm((prev) => ({ ...prev, [name]: value }));
//         setErrors(prev => ({ ...prev, [name]: '' }));

//         // 🔄 실시간 중복체크
//         if (name === 'nickname' || name === 'email') {
//             Id_Check_Api(name, value);
//         }
//     };

//     const pad2 = (s) => s.toString().padStart(2, "0");

//         const isLeapYear = (y) => {
//         const year = parseInt(y, 10);
//         if (Number.isNaN(year) || y.length !== 4) return false;
//         return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
//         };

//         const maxDayOf = (yyyy, mm) => {
//         const m = parseInt(mm, 10);
//         if (Number.isNaN(m)) return 31;

//         if ([4, 6, 9, 11].includes(m)) return 30;
//         if (m === 2) return isLeapYear(yyyy) ? 29 : 28;
//         return 31;
//         };

//         // ✅ 입력 중: 월 00→01 보정, 일 00→01 보정, 월별 최대일 초과는 입력 차단
//         const onBirthChange = (e) => {
//         let raw = e.target.value.replace(/\D/g, "");
//         if (raw.length > 8) raw = raw.slice(0, 8);

//         const yyyy = raw.slice(0, 4);
//         let mm = raw.slice(4, 6);
//         let dd = raw.slice(6, 8);

//         // 월 2자리 들어오면 보정 (00 -> 01, 13+ -> 12)
//         if (mm.length === 2) {
//             let m = parseInt(mm, 10);
//             if (Number.isNaN(m) || m <= 0) m = 1; // ✅ 00 -> 01
//             if (m > 12) m = 12;
//             mm = pad2(m);
//         }

//         // 일 2자리 들어오면 보정/차단
//         if (dd.length === 2) {
//             let d = parseInt(dd, 10);
//             if (Number.isNaN(d) || d <= 0) d = 1; // ✅ 00 -> 01

//             // 월이 아직 2자리 완성 안 됐으면(입력 중) 31까지만 우선 제한
//             if (mm.length < 2) {
//             if (d > 31) return; // 입력 차단
//             dd = pad2(d);
//             } else {
//             const maxD = maxDayOf(yyyy, mm);
//             if (d > maxD) return; // ✅ 월별 최대일 초과 입력 차단
//             dd = pad2(d);
//             }
//         }

//         // YYYY/MM/DD 형태로 구성 (입력 중엔 가능한 만큼만 표시)
//         let formatted = yyyy;
//         if (raw.length >= 5) formatted += "/" + mm;
//         if (raw.length >= 7) formatted += "/" + dd;

//         setForm((prev) => ({ ...prev, birth: formatted }));
//         };

//         // ✅ blur 시: 무조건 ####/##/##로 정리 + 월/일 보정 + 월별 최대일로 보정
//         const onBirthBlur = () => {
//         const raw = (form.birth || "").replace(/\D/g, "").slice(0, 8);

//         const yyyy = raw.slice(0, 4);
//         let mm = raw.slice(4, 6);
//         let dd = raw.slice(6, 8);

//         // 연도가 4자리 아닐 때는 형식 강제하지 않게 할 수도 있음
//         // 여기서는 "무조건" 원한다 했으니 부족하면 0으로 채움
//         const yFixed = yyyy.padEnd(4, "0");

//         // 월 보정
//         let m = parseInt(mm || "0", 10);
//         if (Number.isNaN(m) || m <= 0) m = 1; // ✅ 00/빈값 -> 01
//         if (m > 12) m = 12;
//         const mFixed = pad2(m);

//         // 일 보정
//         let d = parseInt(dd || "0", 10);
//         if (Number.isNaN(d) || d <= 0) d = 1; // ✅ 00/빈값 -> 01

//         const maxD = maxDayOf(yFixed, mFixed);
//         if (d > maxD) d = maxD; // ✅ blur에서는 자연스럽게 최대일로 보정
//         const dFixed = pad2(d);

//         setForm((prev) => ({
//             ...prev,
//             birth: `${yFixed}/${mFixed}/${dFixed}`,
//         }));
//         };



//     //데이터 check폼에 저장해주기
//     const onAgreeChange = (e) => {
//         const { name, checked } = e.target;
//         setAgree((prev) => ({ ...prev, [name]: checked }));
//     };



//     //지금까지 만든 함수 이용해서 최종 API연동 회원가입 구현 조건
//     const onSubmit = async(e) => {
//         e.preventDefault();

//         if (!requiredOk) {
//             alert("필수 입력/필수 약관 동의를 확인해주세요.");
//             return;
//         }
//         if (form.password !== form.password2) {
//             alert("비밀번호가 일치하지 않습니다.");
//             return;
//         }

//         try {
//             const birthdateClean = form.birth
//                 .replace(/[^0-9]/g, '')
//                 .substring(0, 8)
//                 .replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3') || null;

//             const payload = {
//                 nickname: form.nickname,
//                 email: form.email,
//                 password: form.password,
//                 birthdate: birthdateClean,  // YYYY-MM-DD 변환
//             };

//             const result = await New_User(payload);
//             if (result.success) {
//                 alert("회원가입이 완료되었습니다.");
//                 Navigate("/login");
//             }
//         } catch (error) {
//             alert(error.response?.data?.error || '회원가입 실패');
//         }
//     };

//     //중복확인 버튼 클릭시 실시
//     const handleCheckDuplicate = (type) => {
//         if (form[type].length < 2) {
//             alert('2글자 이상 입력해주세요.');
//             return;
//         }
//         Id_Check_Api(type, form[type]);
//     };

//     // 본체 시작
//     return (
//         <div className="signup-bs-page">
//             <Container className="py-4" style={{ maxWidth: 1000 }}>
//                 {/* 소셜 로그인 영역 */}
//                 <div className="text-center mb-3">
//                     <div className="small mb-3 sns_login_text">복잡한 입력없이 3초만에 회원가입 OK!</div>

//                     <div className="d-grid gap-2 mx-auto signup-bs-sns" style={{ maxWidth: 380 }}>
//                         <Button className="signup-bs-btn-naver" size="lg" type="button">
//                             <span className="signup-bs-badge">N</span>
//                             네이버로 계속하기
//                         </Button>

//                         <Button className="signup-bs-btn-kakao" size="lg" type="button">
//                             <span className="sinup-bs-badge"><FaComment /></span>
//                             카카오로 계속하기
//                         </Button>

//                         <Button variant="light" className="signup-bs-btn-google" size="lg" type="button">
//                             <span className="signup-bs-btn-badge google"><FaGoogle /></span>
//                             구글로 계속하기
//                         </Button>
//                     </div>

//                     <div className="mt-3 small text-muted">간편 가입 아이디가 없으면</div>
//                     <div className="signup-bs-arrow mt-1">
//                         <span>▼</span> 아래 회원가입 정보를 입력해주세요. <span>▼</span>
//                     </div>
//                 </div>

//                 <div className="signup-bs-divider my-3" />

//                 {/* 회원정보 시작 */}
//                 <Form onSubmit={onSubmit}>
//                     {/* 1:회원정보(필수) */}
//                     <Card className="mb-3 border-0">
//                         <Table responsive className="mb-0 align-middle signup-bs-table">
//                             <tbody>
//                                 <tr>
//                                     <td className="signup-bs-left">회원정보(필수)</td>

//                                     <td className="signup-bs-mid">
//                                         <div className="signup-bs-grid">

//                                             {/* 닉네임: 실시간+수동 중복체크 */}
//                                             <div className="signup-bs-label">닉네임</div>
//                                             <InputGroup size="sm">
//                                                 <Form.Control name="nickname" value={form.nickname} onChange={onChange}
//                                                     className={errors.nickname ? 'is-invalid' : available.nickname === true ? 'is-valid' : ''}
//                                                     placeholder="닉네임을 입력해주세요."/>
//                                             {/* 중복체크 확인시 변하는 css*/}
//                                                 <Button
//                                                     type="button" className={`signup-bs-mini ${checking.nickname ? 'text-white bg-primary' : ''}`}
//                                                     onClick={() => handleCheckDuplicate('nickname')} disabled={checking.nickname}>
//                                                     {checking.nickname ? ( <span className="spinner-border spinner-border-sm" /> ) : '중복확인'}
//                                                 </Button>
//                                             </InputGroup>
//                                             {/* 에러메세지 */}
//                                             {errors.nickname && <div className="form-text text-danger small mb-2">{errors.nickname}</div>}
//                                             {available.nickname === true && <div className="form-text text-success small mb-2">사용 가능한 닉네임입니다.</div>}

//                                             {/*이메일: 실시간+수동 중복체크 */}
//                                             <div className="signup-bs-label">아이디 (email)</div>
//                                             <InputGroup size="sm">
//                                                 <Form.Control name="email" type="email" value={form.email} onChange={onChange}
//                                                     className={errors.email ? 'is-invalid' : available.email === true ? 'is-valid' : ''}
//                                                     placeholder="example@email.com" />
//                                             {/* 중복체크 확인시 변하는 css*/}
//                                                 <Button
//                                                     type="button" className={`signup-bs-mini ${checking.email ? 'text-white bg-primary' : ''}`}
//                                                     onClick={() => handleCheckDuplicate('email')} disabled={checking.email}>
//                                                     {checking.email ? (<span className="spinner-border spinner-border-sm" />) : '중복확인'}
//                                                 </Button>
//                                             </InputGroup>
//                                             {/* 에러메세지 */}
//                                             {errors.email && <div className="form-text text-danger small mb-2">{errors.email}</div>}
//                                             {available.email === true && <div className="form-text text-success small mb-2">사용 가능한 이메일입니다.</div>}

//                                             {/* 비밀번호 */}
//                                             <div className="signup-bs-label">비밀번호 (8자이상)</div>
//                                             <InputGroup size="sm">
//                                                 <Form.Control type="password" name="password" value={form.password} onChange={onChange} placeholder="비밀번호를 입력해주세요."/>
//                                                 <Button type="button" className="signup-bs-mini">확인</Button>
//                                             </InputGroup>

//                                             <div className="signup-bs-label">비밀번호 확인</div>
//                                             <InputGroup size="sm">
//                                                 <Form.Control type="password" name="password2" value={form.password2} onChange={onChange} placeholder="비밀번호를 한 번 더 입력해주세요." />
//                                                 <Button type="button" className="signup-bs-mini">확인</Button>
//                                             </InputGroup>

//     {/* 생년월일 */}
// <div className="signup-bs-label">생년월일</div>
// <InputGroup size="sm">
//     <Form.Control type="text" name="birth" value={form.birth} onChange={onBirthChange} onBlur={onBirthBlur} placeholder='YYYY/MM/DD' maxLength={10} />
// </InputGroup>
// </div>
//                                     </td>

//                                     <td className="signup-bs-right">
//                                         <div className="signup-bs-avatar">
//                                             <div className="signup-bs-avatar-box">
//                                                 <div className="signup-bs-avatar-icon" />
//                                             </div>
//                                             <div className="d-flex gap-2 mt-2">
//                                                 <Button type="button" size="sm" variant="outline-secondary" className="w-50">파일찾기</Button>
//                                                 <Button type="button" size="sm" className="w-50 signup-bs-mini">업로드</Button>
//                                             </div>
//                                         </div>
//                                     </td>
//                                 </tr>
//                             </tbody>
//                         </Table>
//                     </Card>


//                     {/* 2:약관동의 */}
//                     <Card className="mb-3 border-0">
//                         <Table responsive className="mb-0 align-middle signup-bs-table">
//                             <tbody>
//                                 <tr>
//                                     <td className="signup-bs-left">약관동의</td>
//                                     <td className="signup-bs-mid" colSpan={2}>
//                                         <div className="d-grid gap-2 py-1">
//                                             <Form.Check label="서비스 이용약관 동의 (필수)" name="terms" checked={agree.terms} onChange={onAgreeChange} />
//                                             <Form.Check label="개인정보 처리방침 동의 (필수)" name="privacy" checked={agree.privacy} onChange={onAgreeChange} />
//                                             <Form.Check label="외부 AI 서비스 동의 (필수)" name="thirdParty" checked={agree.thirdParty} onChange={onAgreeChange} />
//                                             <Form.Check label="마케팅 정보 수신 (선택)" name="marketing" checked={agree.marketing} onChange={onAgreeChange} />
//                                             <Form.Check label="데이터 분석/로그 수집 (선택)" name="analytics" checked={agree.analytics} onChange={onAgreeChange} />
//                                             <Form.Check label="맞춤 추천을 위한 정보 활용 (선택)" name="recommend" checked={agree.recommend} onChange={onAgreeChange} />
//                                         </div>
//                                     </td>
//                                 </tr>
//                             </tbody>
//                         </Table>
//                     </Card>

//                     {/* 하단 버튼 */}
//                     <div className="d-flex justify-content-end gap-2">
//                         <Button type="button" variant="secondary" onClick={() => Navigate("/login")}>
//                             취소
//                         </Button>
//                         <Button type="submit" className="signup-bs-submit" disabled={!requiredOk}>
//                             회원가입
//                         </Button>
//                     </div>
//                 </Form>
//             </Container>
//         </div>
//     );
// }

import '../../css/User.css'
import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { debounce } from 'lodash';  // 실시간 중복체크 딜레이 처리 아이디 입력시 api 불려와야하는데 너무 빠르게 불러오면 비용up
import { Id_Check, New_User } from '../../api/User_Api';  // API 연동

import { Container, Row, Col, Button, Form, Card, Table, InputGroup, Image } from "react-bootstrap";
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


    // 회원가입 아이콘
    const onKakaoLogin = () => {
        console.log("카카오 로그인 클릭");
    };

    const onNaverLogin = () => {
        console.log("네이버 로그인 클릭");
    };

    const onGoogleLogin = () => {
        console.log("구글 로그인 클릭");
    };

    //필수 약관 체크 할수 있게 하기
    const [agree, setAgree] = useState({
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
        if (type === 'nickname' && value.length < 3) return;
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
    }, [form, agree, available]);



    //데이터 form폼에 저장해주기
    const onChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
        setErrors(prev => ({ ...prev, [name]: '' }));
    };


    //생년월일
    const pad2 = (s) => s.toString().padStart(2, "0");

    const isLeapYear = (y) => {
        const year = parseInt(y, 10);
        if (Number.isNaN(year) || y.length !== 4) return false;
        return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
    };

    const maxDayOf = (yyyy, mm) => {
        const m = parseInt(mm, 10);
        if (Number.isNaN(m)) return 31;

        if ([4, 6, 9, 11].includes(m)) return 30;
        if (m === 2) return isLeapYear(yyyy) ? 29 : 28;
        return 31;
    };

    // ✅ 입력 중: 월 00→01 보정, 일 00→01 보정, 월별 최대일 초과는 입력 차단
    const onBirthChange = (e) => {
        let raw = e.target.value.replace(/\D/g, "");
        if (raw.length > 8) raw = raw.slice(0, 8);

        const yyyy = raw.slice(0, 4);
        let mm = raw.slice(4, 6);
        let dd = raw.slice(6, 8);

        // 월 2자리 들어오면 보정 (00 -> 01, 13+ -> 12)
        if (mm.length === 2) {
            let m = parseInt(mm, 10);
            if (Number.isNaN(m) || m <= 0) m = 1; // ✅ 00 -> 01
            if (m > 12) m = 12;
            mm = pad2(m);
        }

        // 일 2자리 들어오면 보정/차단
        if (dd.length === 2) {
            let d = parseInt(dd, 10);
            if (Number.isNaN(d) || d <= 0) d = 1; // ✅ 00 -> 01

            // 월이 아직 2자리 완성 안 됐으면(입력 중) 31까지만 우선 제한
            if (mm.length < 2) {
                if (d > 31) return; // 입력 차단
                dd = pad2(d);
            } else {
                const maxD = maxDayOf(yyyy, mm);
                if (d > maxD) return; // ✅ 월별 최대일 초과 입력 차단
                dd = pad2(d);
            }
        }

        // YYYY/MM/DD 형태로 구성 (입력 중엔 가능한 만큼만 표시)
        let formatted = yyyy;
        if (raw.length >= 5) formatted += "/" + mm;
        if (raw.length >= 7) formatted += "/" + dd;

        setForm((prev) => ({ ...prev, birth: formatted }));
    };

    // ✅ blur 시: 무조건 ####/##/##로 정리 + 월/일 보정 + 월별 최대일로 보정
    const onBirthBlur = () => {
        const raw = (form.birth || "").replace(/\D/g, "").slice(0, 8);

        const yyyy = raw.slice(0, 4);
        let mm = raw.slice(4, 6);
        let dd = raw.slice(6, 8);

        // 연도가 4자리 아닐 때는 형식 강제하지 않게 할 수도 있음
        // 여기서는 "무조건" 원한다 했으니 부족하면 0으로 채움
        const yFixed = yyyy.padEnd(4, "0");

        // 월 보정
        let m = parseInt(mm || "0", 10);
        if (Number.isNaN(m) || m <= 0) m = 1; // ✅ 00/빈값 -> 01
        if (m > 12) m = 12;
        const mFixed = pad2(m);

        // 일 보정
        let d = parseInt(dd || "0", 10);
        if (Number.isNaN(d) || d <= 0) d = 1; // ✅ 00/빈값 -> 01

        const maxD = maxDayOf(yFixed, mFixed);
        if (d > maxD) d = maxD; // ✅ blur에서는 자연스럽게 최대일로 보정
        const dFixed = pad2(d);

        setForm((prev) => ({
            ...prev,
            birth: `${yFixed}/${mFixed}/${dFixed}`,
        }));
    };



    //데이터 check폼에 저장해주기
    const onAgreeChange = (e) => {
        const { name, checked } = e.target;
        setAgree((prev) => ({ ...prev, [name]: checked }));
    };



    //지금까지 만든 함수 이용해서 최종 API연동 회원가입 구현 조건
    const onSubmit = async (e) => {
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
        if (form[type].length < 3) {
            alert('3글자 이상 입력해주세요.');
            return;
        }
        Id_Check_Api(type, form[type]);
    };

    // 본체 시작
    return (
        <div className="signup-bs-page">
            <Container style={{ maxWidth: 1000 }}>
                {/* 소셜 로그인 영역 */}
                <div className="text-center">
                    <div className="small mb-3 sns_login_text">복잡한 입력없이 3초만에 회원가입 OK!</div>

                    <div className="social-login">
                        <button type="button" className="social-btn kakao" onClick={onKakaoLogin}>
                            <Image src="/img/kakao_logo.png" alt="" className="social-icon" />
                            <span className="social-text">카카오로 로그인</span>
                        </button>

                        <button type="button" className="social-btn naver" onClick={onNaverLogin}>
                            <Image src="/img/naver_logo.png" alt="" className="social-icon naver" />
                            <span className="social-text">네이버로 로그인</span>
                        </button>

                        <button type="button" className="social-btn google" onClick={onGoogleLogin}>
                            <Image src="/img/google_logo.png" alt="" className="social-icon" />
                            <span className="social-text">구글로 로그인</span>
                        </button>
                    </div>



                    <div className="mt-3 small text-muted">간편 가입 아이디가 없으면</div>
                    <div className="signup-bs-arrow mt-1">
                        <span>▼</span> 아래 회원가입 정보를 입력해주세요. <span>▼</span>
                    </div>
                </div>


                {/* 회원가입 시작 */}
                <div className='signup_all'>
                    <div className='signup_box_all'>
                        <div className='signup_box'>
                            <div className='signup_box_title'>
                                <h4>회원가입</h4>
                            </div>

                            {/* 닉네임 */}
                            <div className="join-row mt-5">
                                <div className="join-label">
                                    닉네임 <span className="req">*</span>
                                </div>

                                <div className="join-field">
                                    <InputGroup size="sm" className="join-ig">
                                        <Form.Control name="nickname" value={form.nickname} onChange={onChange}
                                            className={errors.nickname ? 'is-invalid' : available.nickname === true ? 'is-valid' : ''}
                                            placeholder="닉네임을 입력해주세요." />

                                        <Button
                                            type="button" className={`join-btn-outline ${checking.nickname ? 'text-white bg-primary' : ''}`}
                                            onClick={() => handleCheckDuplicate('nickname')} disabled={checking.nickname}>
                                            {checking.nickname ? (<span className="spinner-border spinner-border-sm" />) : '중복확인'}
                                        </Button>
                                    </InputGroup>

                                    {errors.nickname && <div className="form-text text-danger small mb-2">{errors.nickname}</div>}
                                    {available.nickname === true && <div className="form-text text-success small mb-2">사용 가능한 닉네임입니다.</div>}
                                </div>
                            </div>

                            {/* 아이디 */}
                            <div className="join-row">
                                <div className="join-label">
                                    아이디 (email) <span className="req">*</span>
                                </div>

                                <div className="join-field">
                                    <InputGroup size="sm" className="join-ig">
                                        <Form.Control name="email" type="email" value={form.email} onChange={onChange}
                                            className={errors.email ? 'is-invalid' : available.email === true ? 'is-valid' : ''}
                                            placeholder="예: marketkurly@kurly.com" />

                                        <Button
                                            type="button" className={`join-btn-outline ${checking.email ? 'text-white bg-primary' : ''}`}
                                            onClick={() => handleCheckDuplicate('email')} disabled={checking.email}>
                                            {checking.email ? (<span className="spinner-border spinner-border-sm" />) : '중복확인'}
                                        </Button>
                                    </InputGroup>

                                    {errors.email && <div className="form-text text-danger small mb-2">{errors.email}</div>}
                                    {available.email === true && <div className="form-text text-success small mb-2">사용 가능한 이메일입니다.</div>}
                                </div>
                            </div>


                            {/* 비밀번호 */}
                            <div className="join-row">
                                <div className="join-label">
                                    비밀번호 (8자 이상) <span className="req">*</span>
                                </div>

                                <div className="join-field">
                                    <Form.Control size='sm' type="password" name="password" value={form.password} onChange={onChange} placeholder="비밀번호를 입력해주세요." className="join-input" />
                                </div>
                            </div>

                            {/* 비밀번호 확인 */}
                            <div className="join-row">
                                <div className="join-label">
                                    비밀번호확인 <span className="req">*</span>
                                </div>

                                <div className="join-field">
                                    <Form.Control size='sm' type="password" name="password2" value={form.password2} onChange={onChange} placeholder="비밀번호를 한 번 더 입력해주세요." className="join-input" />
                                </div>
                            </div>



                            {/* 생년월일 */}
                            <div className="join-row mb-5">
                                <div className="join-label">생년월일</div>

                                <div className="join-field">
                                    <Form.Control size="sm"
                                        type="text"
                                        name="birth"
                                        value={form.birth}
                                        onChange={onBirthChange}
                                        onBlur={onBirthBlur}
                                        placeholder="YYYY/MM/DD"
                                        maxLength={10}
                                        inputMode="numeric"
                                        className="join-input" />
                                </div>
                            </div>
                        </div>
                        <div className='signup_checkbox'>
                            <div className='signup_checkbox_title join-label '>이용약관동의 <span className="req">*</span>
                            </div>
                            <div className='signup_checkbox_all_content'>
                                <div colSpan={2}>
                                    <div className="signup_check_content d-grid gap-1 py-1">
                                        <Form.Check label="서비스 이용약관 동의 (필수)" name="terms" checked={agree.terms} onChange={onAgreeChange} />
                                        <Form.Check label="개인정보 처리방침 동의 (필수)" name="privacy" checked={agree.privacy} onChange={onAgreeChange} />
                                        <Form.Check label="외부 AI 서비스 동의 (필수)" name="thirdParty" checked={agree.thirdParty} onChange={onAgreeChange} />
                                        <Form.Check label="마케팅 정보 수신 (선택)" name="marketing" checked={agree.marketing} onChange={onAgreeChange} />
                                        <Form.Check label="데이터 분석/로그 수집 (선택)" name="analytics" checked={agree.analytics} onChange={onAgreeChange} />
                                        <Form.Check label="맞춤 추천을 위한 정보 활용 (선택)" name="recommend" checked={agree.recommend} onChange={onAgreeChange} />
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="signup_button">
                            <Button type="button" variant="secondary" onClick={() => Navigate("/login")}>
                                취소
                            </Button>
                            <Button type="submit" className="signup-bs-submit" disabled={!requiredOk}>
                                회원가입
                            </Button>
                        </div>
                    </div>
                </div>
            </Container>
        </div>
    );
}

// 간편회원가입 흰색 하고 이용약관 색 추가 & ㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗㅗ