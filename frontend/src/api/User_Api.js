// src/api/userApi.js
import axios from 'axios';


// =====  User전용 API  ============================
const protectedApi = axios.create({
  baseURL: 'http://localhost:5000/api',
});

//토큰 값을 닉네임으로 지정해주기
protectedApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");  // ✅ 통일된 키 이름
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;  // Bearer john123
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 추후에 사용예정: 401에러시 자동 로그아웃
protectedApi.interceptors.response.use(
  (response) => response,
  (error) => {
    //if ([401, 403].includes(error.response?.status)) { 나중에 2개 이상 에러에도 적용하고 싶을때 쓸 코드
    if (error.response?.status === 401) {
      AuthUtils.logout();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

//보호된 API 함수들 사용법
export const getProfile = () => protectedApi.get('/profile');
export const getPosts = () => protectedApi.get('/posts');

// === 비user 전용 함수들 ==============================================

// =====  비user 전용 API  =====
const publicApi = axios.create({
  baseURL: 'http://localhost:5000/api',
});

// 1. 닉네임 이메일 중복 체크 API
export async function Id_Check(type, value) {
  const res = await publicApi.get(`/users/check/${type}`, {
    params: { value }
  });
  return res.data;  // 데이터형식  예시 { 가능여부: true/false, 에러메세지 : "..." }
}


// 2. 회원가입 API
export async function New_User(formData) {
  const res = await publicApi.post('/users', formData);
  return res.data;  // 데이터형식  예시 {성공여부 :메세지}
}


// 3. 로그인 API
export const loginUser = async (email, password) => {
    const response = await publicApi.post("/users/login", {email,password});
    return response.data;      // 데이터 형식 { success, message }
}
//=============================================================================



// ===== 인증 유틸리티 ==========================================================
export const AuthUtils = {
  login: (nickname) => {
    console.log(`🔐 로그인: 토큰 "${nickname}" 저장`);
    localStorage.setItem("authToken", nickname);
    window.dispatchEvent(new Event("auth-change"));
  },
  logout: () => {
    console.log('🔓 로그아웃: 토큰 삭제 시작');
    const beforeToken = localStorage.getItem("authToken");
    localStorage.removeItem("authToken");
    console.log(`✅ 토큰 삭제 완료: "${beforeToken}" → 없음`);
    window.dispatchEvent(new Event("auth-change"));
  },
  isLoggedIn: () => !!localStorage.getItem("authToken"),
  getNickname: () => localStorage.getItem("authToken")
};
//=============================================================================