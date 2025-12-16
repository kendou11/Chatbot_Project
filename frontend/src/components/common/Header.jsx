import React from "react";
import { useNavigate } from "react-router-dom";
import { Navbar, Nav, Container } from "react-bootstrap";


const Header = () => {
  const navigate = useNavigate()

  return (
    <div className="Header-all">
      <Navbar expand="lg" className="header-all" >
        <Container fluid="lg" style={{ marginTop:"-8px",height:"74px", width: "1200px", backgroundColor: "#F9EEFF" }}>
          <Navbar.Brand href="/">
            <img src="/img/Top_logo.png" alt="logo" className="logo" />
          </Navbar.Brand>

          <Navbar.Toggle aria-controls="basic-navbar-nav" />

          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="ms-auto login-menu">
              <Nav.Link onClick={()=>{navigate('/Login')}}>로그인</Nav.Link>
              <Nav.Link onClick={()=>{navigate('/Signup')}}>회원가입</Nav.Link>
              <Nav.Link onClick={()=>{navigate('/ChatList')}}>대화목록</Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    </div>
  );
};

export default Header;