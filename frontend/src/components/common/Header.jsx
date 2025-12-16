import React from "react";

const Header = () => {
  return (
    <div className="Header-all">
        <nav className="nav-logo">
          <img src={'/img/Top_logo.png'} alt="logo" className="logo" />
          <div>
            <p className="login-menu">로그인 / 회원가입 / 개인비서</p>
          </div>
        </nav>
    </div>
  );
};

export default Header;