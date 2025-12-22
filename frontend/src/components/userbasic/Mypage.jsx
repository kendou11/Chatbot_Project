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
                        <h2 className='mb-4 mt-4'>마이페이지</h2>
                        <div className='mypage-box'></div>

                        
                        <div className='mypage-moneybox mb-3 mt-4'>
                            <div className='mypage-money'>현재 잔액</div>
                            <Button variant="primary">충전하기</Button>
                        </div>

                    </Col>
                </Row>

                <Row >
                    <Col xs={12} md={6}>
                        <div className='mypage-membership mb-3'>
                            <h3>개인비서</h3>
                            <Row>
                            <div className="membership_circle_div" style={{justifyContent:'space-around', paddingBottom:'0px'}}>
                                <Image src="/img/membership_img.png" roundedCircle className="w-25 mx-1" />
                                <Image src="/img/membership_img.png" roundedCircle className="w-25 mx-1" />
                            </div>
                            </Row>
                            <Row>
                            <div className="membership_circle_div" style={{justifyContent:'space-around', paddingBottom:'25px'}}>
                                <Image src="/img/membership_img.png" roundedCircle className="w-25 mx-1" />
                                <Image src="/img/membership_plus_img.png" roundedCircle className="w-25 mx-1" />
                            </div>
                            </Row>
                        </div>
                    </Col>

                    <Col xs={12} md={6}>
                    <div className='mypage-membership1'>
                        <h3 className='mb-2'>개인정보 변경</h3>
                        <Form.Label>닉네임 변경</Form.Label>
                        <InputGroup className="mb-1">
                                <Form.Control
                                    placeholder="닉네임 변경"
                                    aria-describedby="basic-addon2"
                                />
                                <Button variant="outline-secondary" id="button-addon2">
                                    변경
                                </Button>
                            </InputGroup>

                            <Form.Label>비밀번호 변경</Form.Label>
                            <InputGroup className="mb-1">
                                <Form.Control
                                    type='password'
                                    placeholder="비밀번호 변경"
                                    aria-describedby="basic-addon2"
                                />
                                <Button variant="outline-secondary" id="button-addon2">
                                    변경
                                </Button>
                            </InputGroup>
                            <Form.Label>프로필 이미지 변경</Form.Label>
                            <InputGroup className="mb-1">
                                <Form.Control type="file" />
                                <Button variant="outline-secondary" id="button-addon2">
                                    변경
                                </Button>
                            </InputGroup>
                            <Button variant="danger" className="mt-2">회원탈퇴</Button>
                            <Button variant="danger" className="mx-3 mt-2" disabled>멤버십 해지하기</Button>
                        </div>
                    </Col>
                </Row>
            </Container>
        </div>
    );
}

export default Mypage
