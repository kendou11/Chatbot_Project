import React from "react";
import { Navbar, Container } from "react-bootstrap";

const Footer = () => {
  return (
    <Navbar className="Footer_navBar">
      <Container className="justify-content-center" style={{ width: "1200px", height: "45px", backgroundColor: "#e8e8e8ff", margin: "-10px auto"}} >
        <Navbar.Brand href="/" style={{ fontSize: "15px" }}>
          © 2025. AI Service. Jumbo Mandu, inc.
        </Navbar.Brand>
      </Container>
    </Navbar>
  );
};

export default Footer;