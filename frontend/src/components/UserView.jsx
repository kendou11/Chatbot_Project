// src/components/UserView.jsx
import React from 'react';

// test용 보기
export function TestView({ test }) {
  return (
    <section>
      <h2>/api/test 결과 (GET)</h2>
      <p>{test}</p>
    </section>
  );
}

// 유저 리스트 get 으로 불러와서 보는법 초기 세팅
export function UserListView({ users }) {
  return (
    <section>
      <h2>/api/users 결과 (GET)</h2>
      <ul>
        {users.map((u) => (
          <li key={u.id}>{u.name} - {u.email}</li>
        ))}
      </ul>
    </section>
  );
}


// 유저정보 추가하는 함수
export function UserFormView({ name, email, onChangeName, onChangeEmail, onSubmit }) {
  return (
    <section>
      <h2>유저 추가 (POST /api/users)</h2>
      <form onSubmit={onSubmit}>
        <input
          placeholder="이름"
          value={name}
          onChange={onChangeName}
        />
        <input
          placeholder="이메일"
          type="email"
          value={email}
          onChange={onChangeEmail}
        />
        <button type="submit">추가</button>
      </form>
    </section>
  );
}
