import { Navbar, Nav, Container } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { AuthUtils } from "../../api/User_Api";

const Header = () => {
  const navigate = useNavigate();
  const [login, setLogin] = useState(false);

  useEffect(() => {
    const syncAuth = () => {setLogin(AuthUtils.isLoggedIn());};
    window.addEventListener("auth-change", syncAuth);
    syncAuth();

    return () => window.removeEventListener("auth-change", syncAuth);
  }, []);

  const handleLogout = () => {
    AuthUtils.logout();
    navigate("/");
  };

  return (
    <Navbar expand="lg" className="header-all-div" style={{ padding: "0" }}>
      <Container fluid className="header-container">
        <Navbar.Brand href="/">
          <img src="/img/Top_logo.png" alt="logo" className="logo" />
        </Navbar.Brand>

        <Navbar.Toggle aria-controls="basic-navbar-nav" />

        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto login-menu">
            {!login ? (
              <>
                <Nav.Link href="/Login">로그인</Nav.Link>
                <Nav.Link href="/Signup">회원가입</Nav.Link>
                {/* 로그인 전엔 대화목록 못가게 Login으로 보내는 거 유지 */}
              </>
            ) : (
              <>
                <Nav.Link as="button" onClick={handleLogout} style={{ background: "none", border: "none", padding: "8" }}>
                  로그아웃
                </Nav.Link>
                <Nav.Link href="/MyPage">마이페이지</Nav.Link>
                <Nav.Link href="/ChatList">대화목록</Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header;
