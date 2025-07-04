import './App.css';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Register from './pages/Register';
import Login from './pages/Login';
import Homepage from './pages/Homepage';
import ErrorPage from './pages/Errorpage';
import Home from './pages/Home';
import AboutUs from './pages/Aboutpage'

import AuthMiddleware from './middleware/Auth';
import PersistLogin from './components/PersistLogin';

function App() {
  return (
      
      <Router>
          <Routes>
            <Route path='/' element={<PersistLogin/>}>
              <Route path="/about" element={<AboutUs/>} />
              <Route path="/homepage" element={<Homepage/>} />
              <Route path="/register" element={<Register/>} />
              <Route path="/login" element={<Login/>} />
              <Route path="/error" element={<ErrorPage/>} />
              <Route element={<AuthMiddleware />}>
                <Route path='/home' index element={<Home />}></Route>
              </Route>
           

            </Route>


              <Route
                path="*"
                element={<Navigate to="/error" state={{ code: 404, message: "Page Not Found" }} replace />}
              />

          </Routes>
      </Router>
  );
}

export default App;
