import React from "react";
import { Container, Row, Col, Image } from "react-bootstrap";


const AIIntroduce = () => {
    return (
        <section>
            <div className="Introduce">
                <Image src='/img/main_slider_img.png' alt="웹사이트_설명" className="AI_introduce_img" fluid />
            </div>

            <div className="service_section">
                <div className="membership_img">
                    <Container >
                        <Row>
                            <Col xs={6} md={4}>
                                <Image src='/img/Membership.gif' alt="멤버십_가입_소개_gif파일" className="membership_gif" roundedCircle />
                            </Col>
                        </Row>
                    </Container>
                </div>
            </div>

            <div className="container text-center my-5">
            <h2>AI 카테고리</h2>
                <div className="d-flex justify-content-center gap-4 mt-4 flex-wrap">
                    <div className="circle-sm bg-secondary text-white d-flex justify-content-center align-items-center">
                    법률 AI
                    </div>
                    <div className="circle-sm bg-secondary text-white d-flex justify-content-center align-items-center">
                    의료 AI
                    </div>
                    <div className="circle-sm bg-secondary text-white d-flex justify-content-center align-items-center">
                    심리 AI
                    </div>
                    <div className="circle-sm bg-secondary text-white d-flex justify-content-center align-items-center">
                    의류 AI
                    </div>
                    <div className="circle-sm bg-secondary text-white d-flex justify-content-center align-items-center">
                    인공지능 AI
                    </div>
                </div>
        </div>
        <div className="Membership-category" style={{padding: "60px 0", textAlign: "center"}}>
      <h2>개인비서 카테고리</h2>
        <div className="d-flex justify-content-center gap-5 mt-4 flex-wrap">
            <div className="circle-lg bg-secondary text-white d-flex justify-content-center align-items-center">
            심리 AI
            </div>
            <div className="circle-lg bg-secondary text-white d-flex justify-content-center align-items-center">
            의류 AI
            </div>
            <div className="circle-lg bg-secondary text-white d-flex justify-content-center align-items-center">
            인공지능 AI
            </div>
        </div>
    </div>
        </section>
    );
};

export default AIIntroduce;