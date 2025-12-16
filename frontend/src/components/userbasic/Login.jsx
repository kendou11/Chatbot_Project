import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate()

  const onSubmit = (e) => {
    // axios 로그인 연결
    console.log({ username, password });
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-avatar">
          {/* 아이콘 이미지 public에 넣고 아래 src만 바꾸기 */}
          <img src="/img/Login_logo.png" alt="avatar" />
        </div>

        <from onSubmit={ onSubmit } className="login-form">
          <label className="login-label">아이디</label>
          <input className="login-input" value={ username } onChange={(e) => setUsername(e.target.value)} placeholder=""/>

          <label className="login-label">비밀번호</label>
          <input className="login-input" value={ password } onChange={(e) => setPassword(e.target.value)} placeholder=""/>

          <button type="button" className="login-forgot">
            비밀번호를 잊으셨나요?
          </button>
          <button type="button" className="btn-login">로그인</button>
          <button type="button" className="btn-signup" onClick={()=>{navigate('/Signup')}}>회원가입</button>

          <div className="social-row">
            <button type="button" className="social N">N</button>
            <button type="button" className="social K">K</button>
            <button type="button" className="social G">G</button>
          </div>
        </from>
      </div>
    </div>
  )
}