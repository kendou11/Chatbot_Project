import React, { useEffect, useState } from 'react';
import { Test_api, User_api, createUser } from './api/User_Api';  //api 불러온거 사용하기 위한 코드
import { TestView, UserListView, UserFormView } from './components/UserView';
import axios from 'axios';


function App() {
    const [test, setTest] = useState('');
        useEffect(() => {
        const loadTest = async () => {
            const data = await Test_api(); // 비동기 호출
            setTest(data.msg);            // 끝나면 state 업데이트 → 재렌더
        };
        loadTest();
    }, []);

    const [user, setUser] = useState([]);
        useEffect(() => {
        const loaduser = async () => {
            const data = await User_api(); // 비동기 호출
            setUser(data);            // 끝나면 state 업데이트 → 재렌더
        };
        loaduser();
    }, []);


    const [name, setName]   = useState('');
    const [email, setEmail] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault(); //새로고침 막아주는 코드
        await createUser(name, email);  // ← 여기서 POST 호출
        setName('');
        setEmail('');
    };

    return (
        <>
        <TestView test={test} />
        <UserListView users={user} />
        <UserFormView
              name={name}
              email={email}
              onChangeName={(e) => setName(e.target.value)}
              onChangeEmail={(e) => setEmail(e.target.value)}
              onSubmit={handleSubmit}/>
        </>
        )
}

export default App;
