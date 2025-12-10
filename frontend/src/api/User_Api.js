// src/api/userApi.js
import axios from 'axios';

// 공통 axios 주소
const api = axios.create({
  baseURL: 'http://localhost:5000/api',  // 백엔드 Flask 주소
});

//test 호출
export async function Test_api() {
  const res = await api.get('/test');
  return res.data;   // { msg: "Flask OK" }
}

//users GET 호출
export async function User_api() {
  const res = await api.get('/users');
  return res.data;
}

//user POST 호출
export async function createUser(name, email) {
  const res = await api.post('/users', { name, email });
  return res.data;
}