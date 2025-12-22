import React from 'react'
import { Container, Row, Col, Image, Form, InputGroup, Button } from 'react-bootstrap';

const Mypage = () => {
    return (
        <div className='mypage-content'>
            <Container>
                <Row>
                    <Col xs={6} md={4}>
                        <Image src="/img/logo.png" rounded className='mypage-img' />
                    </Col>

                    <Col xs={12} md={8}>
                        <Form.Label>닉네임 변경</Form.Label>
                        <InputGroup className="mb-4">
                            <Form.Control
                                placeholder="Recipient's username"
                                aria-describedby="basic-addon2"
                                style={{ maxWidth: '250px' }}
                            />
                            <Button variant="outline-secondary" id="button-addon2">
                                Button
                            </Button>
                        </InputGroup>
                        
                        <div className='mypage-moneybox'>
                            <div className='mypage-money'>현재 잔액</div>
                            <Button variant="primary">Primary</Button>

                        </div>

                    </Col>
                </Row>

                <Row >
                    <Col xs={12} md={6}>
                        <div>
                            <h3>개인비서</h3>
                            <Row>
                            <div className="membership_circle_div" style={{justifyContent:'space-around', paddingBottom:'0px'}}>
                                <Image src="/img/membership_img.png" roundedCircle className="w-25 mx-1" />
                                <Image src="/img/membership_img.png" roundedCircle className="w-25 mx-1" />
                            </div>
                            </Row>
                            <Row>
                            <div className="membership_circle_div" style={{justifyContent:'space-around'}}>
                                <Image src="/img/membership_img.png" roundedCircle className="w-25 mx-1" />
                                <Image src="/img/membership_plus_img.png" roundedCircle className="w-25 mx-1" />
                            </div>
                            </Row>
                        </div>
                    </Col>

                    <Col xs={12} md={6}>
                        <Form.Label>비밀번호 변경</Form.Label>
                        <InputGroup className="mb-1">
                            <Form.Control
                                type='password'
                                placeholder="상수는 술과 고기가 먹고싶다!"
                                aria-describedby="basic-addon2"
                            />
                            <Button variant="outline-secondary" id="button-addon2">
                                Button
                            </Button>
                        </InputGroup>
                        <Form.Label>프로필 이미지 변경</Form.Label>
                        <InputGroup className="mb-1">
                            <Form.Control type="file" />
                            <Button variant="outline-secondary" id="button-addon2">
                                Button
                            </Button>
                        </InputGroup>
                        <Button variant="danger" className="mt-2">회원탈퇴</Button>
                        <Button variant="danger" className="mx-3 mt-2" disabled>멤버십 해지하기</Button>
                    </Col>
                </Row>
            </Container>
        </div>
    );
}

export default Mypage
