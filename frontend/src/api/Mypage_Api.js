// src/api/Mypage_Api.js
import axios from 'axios';
import { AuthUtils } from './User_Api';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
});

// AuthUtils 토큰 자동 추가 인터셉터
api.interceptors.request.use((config) => {
  const token = AuthUtils.getNickname();
  if (token) {
    const safeToken = encodeURIComponent(token);
    config.headers.Authorization = `Bearer ${safeToken}`;
  }
  return config;
});


//마이페이지 내에 유저 정보 변경 디버깅까지 완료
export async function updateProfile(updateData) {
  const res = await api.patch('/users/mypage', updateData);

  // 닉네임이 변경된 경우 토큰도 함께 갱신
  const newNick = res.data?.user?.user_nickname;
  if (newNick && newNick !== AuthUtils.getNickname()) {
    AuthUtils.login(newNick);
  }

  return res.data;
}

// 내 정보 조회
export async function getMyProfile() {
  const res = await api.get('/users/mypage');
  return res.data;
}