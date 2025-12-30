import './App.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import { Route, Routes } from 'react-router-dom';
import "@fortawesome/fontawesome-free/css/all.min.css";


import Header from './components/common/Header.jsx'
import Footer from './components/common/Footer.jsx'
import Main from './components/Main.jsx'
import Login from './components/userbasic/Login.jsx'
import Signup from './components/userbasic/Signup.jsx'
import Mypage from './components/userbasic/Mypage.jsx'
import Pay from './components/userbasic/Pay.jsx'
import Detail from './components/Detail.jsx'
import ErrorPage from "./components/common/ErrorPage.jsx"
import NoticeWrite from './components/notice/NoticeWrite.jsx';
import ChatList from './components/chat/ChatList.jsx';
import NoticeDetail from './components/notice/NoticeDetail.jsx';

/* 자동 스크롤 import */
import BackToTop from "./components/common/BackToTop.jsx";
import { Outlet } from "react-router-dom"

/* --- [통합 챗봇 컴포넌트 하나만 import] --- */
import ChatComponent from './components/ChatComponent.jsx';

function App() {

    return (
        <>
        <Header/>
        <Routes>
            <Route path="/" element={<Main />} />
            <Route path="/Login" element={<Login />} />
            <Route path="/Signup" element={<Signup />} />
            <Route path="/Mypage" element={<Mypage />} />
            <Route path="/Pay" element={<Pay />} />
{/*             <Route path='/Detail' element={<Detail />} /> */}
            <Route path="/api/ai/:aiId" element={<Detail />} />
            <Route path='/ErrorPage' element={<ErrorPage />} />
            <Route path='/NoticeWrite' element={<NoticeWrite />} />
            <Route path='/ChatList' element={<ChatList />} />
            <Route path="/notice/:noticeId" element={<NoticeDetail />} />
            {/* --- [통합 챗봇 컴포넌트 type에 맞춰서 적어줘야함] --- */}
            <Route path="/:type" element={<ChatComponent />} />
        </Routes>   
        <Outlet />
        <BackToTop />
        <Footer/>      
        
        </>
        )
}

export default App;
