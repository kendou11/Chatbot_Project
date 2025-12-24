import "../../css/Notice.css";
import '@fortawesome/fontawesome-free/css/all.min.css';

import { useState, useRef, useEffect } from 'react';
import { Container, Form, Button, Row, Col, Image, Alert } from 'react-bootstrap';
import { create_notice } from '../../api/Notice_Api';
import { AuthUtils } from '../../api/User_Api';

const NoticeWrite = () => {
  // 기존 상태들
  const [files, setFiles] = useState([]);
  const [previewImages, setPreviewImages] = useState([]);
  const fileInputRef = useRef(null);

  // 입력값 상태들
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [tags, setTags] = useState('');
  const [price, setPrice] = useState('');

  // 제출 상태
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');
  const [submitStatus, setSubmitStatus] = useState(''); // success/error

  // 이미지 핸들러들 (변경 없음)
  const handleImageChange = (e) => {
    const selectedFiles = Array.from(e.target.files || []);
    setFiles(selectedFiles);
    const urls = selectedFiles.map((file) => URL.createObjectURL(file));
    setPreviewImages(urls);
  };

  useEffect(() => {
    return () => {
      previewImages.forEach((url) => URL.revokeObjectURL(url));
    };
  }, [previewImages]);

  const removeImage = (indexToRemove) => {
    URL.revokeObjectURL(previewImages[indexToRemove]);
    const nextFiles = files.filter((_, i) => i !== indexToRemove);
    const nextPreviews = previewImages.filter((_, i) => i !== indexToRemove);

    setFiles(nextFiles);
    setPreviewImages(nextPreviews);

    const dt = new DataTransfer();
    nextFiles.forEach((f) => dt.items.add(f));
    if (fileInputRef.current) {
      fileInputRef.current.files = dt.files;
    }
  };
  // GPT


  //완벽한 제출 핸들러 (로그인 검증 포함!)
  const handleSubmit = async (e) => {
    e.preventDefault();

    // 1. 기본 정보 입력되었는지 확인하기
    if (!title.trim() || !content.trim()) {
      setSubmitMessage('제목과 내용을 입력해주세요!');
      setSubmitStatus('error');
      return;
    }

    //2. 토큰값있는지 확인하여 게시판 작성가능 여부 확인하기
    if (!AuthUtils.isLoggedIn()) {
      setSubmitMessage('로그인 후 이용해주세요!');
      setSubmitStatus('error');
      setTimeout(() => window.location.href = '/login', 1500);
      return;
    }

    setIsSubmitting(true);
    setSubmitMessage('');

    try {
      // 3. FormData 생성
      const formData = new FormData();
      formData.append('title', title);
      formData.append('content', content);
      formData.append('tags', tags);
      formData.append('price', price || 0);
      files.forEach((file) => formData.append('images', file));

      // 4. API 호출
      const result = await create_notice(formData);

      if (result.success) {
        // 성공!
        setSubmitStatus('success');
        setSubmitMessage('게시글이 성공적으로 등록되었습니다!');

        // 입력값 초기화
        setTitle('');
        setContent('');
        setTags('');
        setPrice('');
        setFiles([]);
        setPreviewImages([]);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } else {
        // 🔥 서버 에러별 처리
        if (result.error?.includes('로그인') || result.error?.includes('토큰')) {
          AuthUtils.logout();  // 토큰 무효화
          setSubmitMessage('로그인 정보가 만료되었습니다. 다시 로그인해주세요.');
          setTimeout(() => window.location.href = '/login', 1500);
        } else {
          setSubmitStatus('error');
          setSubmitMessage(result.error || '등록에 실패했습니다.');
        }
      }

    } catch (error) {
      console.error('제출 에러:', error);
      setSubmitStatus('error');
      setSubmitMessage(error.message || '등록에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // 취소 핸들러 (그대로!)
  const handleCancel = () => {
    if (window.confirm('작성을 취소하시겠습니까?')) {
      setTitle('');
      setContent('');
      setTags('');
      setPrice('');
      setFiles([]);
      setPreviewImages([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      setSubmitMessage('');
      setSubmitStatus('');
    }
  };

  return (
    <div>
      <Container
        className="post-write-container NoticeWrite_all"
        style={{ maxWidth: "900px", marginTop: "40px" }}
      >
        <div className="NW_title_box">
          <h4 className="NW_title">게시글 작성</h4>
        </div>

        {/* 제출 메시지 */}
        {submitMessage && (
          <Alert
            variant={submitStatus === 'success' ? 'success' : 'danger'}
            onClose={() => {
              setSubmitMessage('');
              setSubmitStatus('');
            }}
            dismissible
          >
            {submitMessage}
          </Alert>
        )}

        <Form onSubmit={handleSubmit}>
          {/* 제목 */}
          <Form.Group className="mb-3 NW-sub-title">
            <h6 className="NW-sub-h6">제 목</h6>
            <Form.Control type="text" placeholder="제목을 입력하세요." className="NW-title-text" value={title} onChange={(e) => setTitle(e.target.value)} disabled={isSubmitting}/>
          </Form.Group>

          <Form.Group>
            <div className="mb-4 NW-sub-title">
            <h6 className="NW-sub-h6">사진 첨부</h6>
            <Form.Control
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*"
              onChange={handleImageChange}
              className="NW-title-text1"
              disabled={isSubmitting}
            />
            </div>

            <div className="image-preview-container">
              {previewImages.map((src, index) => (
                <div className="preview-wrapper" key={index}>
                  <button type="button"
                    className="preview-remove-btn NW_Del_button"
                    onClick={() => removeImage(index)}
                    aria-label="이미지 삭제"><i class="fa-solid fa-xmark"></i></button>

                  <Image src={src} thumbnail className="preview-image NW_preview_img" />
                </div>
              ))}
            </div>
          </Form.Group>

          <Form.Group className="mb-4 NW-sub-title NW-content-row">
            <h6 className="NW-sub-h6 NW_content">내 용</h6>
            <Form.Control
              as="textarea"
              rows={10}
              placeholder="내용을 입력하세요."
              className="content-textarea"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
              disabled={isSubmitting}
            />
          </Form.Group>


          <div className="NW_tag_box">
            <Form.Group className="mb-3 NW-sub-title">
              <h6 className="NW-sub-h6">태그 입력</h6>
              <Form.Control type="text" placeholder="# 태그 입력" className="NW-title-text" />
            </Form.Group>

            <Form.Group className="mb-4 NW-sub-title">
              <h6 className="NW-sub-h6">가격 제시</h6>
              <Form.Control type="number" placeholder="₩ 가격 입력" className="NW-title-text" />
            </Form.Group>
          </div>

          {/* 버튼들 */}
          <Row className="justify-content-end">
            <Col xs="auto">
              <Button variant="success" className="NW_check_button" type="submit"><i className="fa-solid fa-check"></i>확인</Button>
            </Col>
            <Col xs="auto">
              <Button variant="secondary" className="NW_cancel_button">취소</Button>
            </Col>
          </Row>
        </Form>
      </Container>
    </div>
  );
};

export default NoticeWrite;
