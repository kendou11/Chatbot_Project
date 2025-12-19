import './App.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import { Route, Routes } from 'react-router-dom';


import Header from './components/common/Header.jsx'
import Footer from './components/common/Footer.jsx'
import Main from './components/Main.jsx'
import Login from './components/userbasic/Login.jsx'
import Signup from './components/userbasic/Signup.jsx'
import Mypage from './components/userbasic/Mypage.jsx'
import Pay from './components/userbasic/Pay.jsx'
import Detail from './components/Detail.jsx'
import ErrorPage from "./components/common/ErrorPage.jsx"

/* 자동 스크롤 import */
import BackToTop from "./components/common/BackToTop.jsx";
import { Outlet } from "react-router-dom"

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
            <Route path='/Detail' element={<Detail />} />
            <Route path='/ErrorPage' element={<ErrorPage />} />
        </Routes>   
        <Outlet />
        <BackToTop />
        <Footer/>      
        
        </>
        )
}

export default App;
