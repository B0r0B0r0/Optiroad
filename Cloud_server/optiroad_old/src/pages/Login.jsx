import { useEffect, useRef, useState, React } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInfoCircle, faCheck, faTimes, faHome } from '@fortawesome/free-solid-svg-icons';

import { axiosInstance } from '../axios/axios'
import useAuth from '../hooks/useAuth'
import './login.css';
import video from '../multimedia/cars3.mp4';


const user_regex = /^[a-zA-Z0-9-_]+$/;
const password_regex = /^[a-zA-Z0-9-_!@#$%]+$/;



const Login = () => {

    const navigate = useNavigate();

    const userRef = useRef();
    const errRef = useRef();

    const location = useLocation()
    const fromLocation = location?.state?.from?.pathname || '/'

    const { setAccessToken, setCSRFToken } = useAuth()

    const [user, setUser] = useState('');
    const [validName, setValidName] = useState(false);  
    const [userFocus, setUserFocus] = useState(false);

    const [password, setPassword] = useState('');
    const [validPassword, setValidPassword] = useState(false);
    const [passwordFocus, setPasswordFocus] = useState(false);

    const [errMsg, setErrMsg] = useState('');
    const [success, setSuccess] = useState(false);

    const handleRegister = () => {
        navigate('/register');
    }

    useEffect(() => {
        userRef.current.focus();
    }, []);
    
    useEffect(() => {
        const result = user_regex.test(user);
        setValidName(result);
    }, [user]);

    useEffect(() => {
        const result = password_regex.test(password);
        setValidPassword(result);
    }, [password]);



    useEffect(() => {
        setErrMsg('');
    }, [user,password]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const v1 = user_regex.test(user);
        const v2 = password_regex.test(password);

        if (!v1 || !v2) {
            setErrMsg('Invalid Entry');
            return;
        }

        try {
            const response = await axiosInstance.post('/login', JSON.stringify({
                username: user,
                password
            }))

            setAccessToken(response?.data?.access_token)
            setCSRFToken(response.headers["x-csrf-token"])
            setUser()
            setPassword()

            navigate('/home')
        } catch (error) {
            navigate('/error', {
                state: {
                    code: error.response?.status || 500,
                    message: error.response?.data?.message || 'Internal Server Error'
                }
            });
        }
        
    }

    const handleHome = () => {
        navigate('/homepage');
    }

    return (
        <div className="homepage">
            <video
                autoPlay
                muted
                loop
                className="background-video"
            >
                <source src={video} type="video/mp4" />
                Your browser does not support the video tag.
            </video>
            <section>
            <a onClick={handleHome} className="home"><FontAwesomeIcon icon={faHome} className='bluetext'/></a>
            <div className="background-overlay"></div>
            <p ref={errRef} className={errMsg ? "errmsg" : "offscreen"} aria-live="assertive"> {errMsg} </p>   
            <h1>Login</h1>
            <form onSubmit={handleSubmit}>
                <label htmlFor='username'> Username: 
                    <span className={validName ? 'valid' : 'hide'}>
                        <FontAwesomeIcon icon={faCheck} />
                    </span>
                    <span className={validName || !user ? 'hide' : 'invalid'}>
                        <FontAwesomeIcon icon={faTimes} />
                    </span>
                </label>
                <input
                    type='text'
                    id='username'
                    ref={userRef}
                    autoComplete='off'
                    onChange={(e) => setUser(e.target.value)}
                    required
                    aria-invalid={!validName}
                    aria-describedby='uidnote'
                    onFocus={() => setUserFocus(true)}
                    onBlur={() => setUserFocus(false)}
                />
                <p id='uidnote' className={ user && !validName ? 'instructions' : 'offscreen'}>
                    <FontAwesomeIcon icon={faInfoCircle} />
                    Only letters, numbers, hyphens, and underscores allowed.
                </p>

                <label htmlFor='password'> 
                    Password:
                    <span className={validPassword ? 'valid' : 'hide'}>
                        <FontAwesomeIcon icon={faCheck} />
                    </span>
                    <span className={validPassword || !password ? 'hide' : 'invalid'}>
                        <FontAwesomeIcon icon={faTimes} />
                    </span>
                </label>
                <input
                    type='password'
                    id='password'
                    autoComplete='off'
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    aria-invalid={!validPassword}
                    aria-describedby='passwordnote'
                    onFocus={() => setPasswordFocus(true)}
                    onBlur={() => setPasswordFocus(false)}
                />
                <p id='passwordnote' className={ password &&  !validPassword ? 'instructions' : 'offscreen'}>
                    <FontAwesomeIcon icon={faInfoCircle} />
                    Allowed characters: letters, numbers 
                                                <span> </span>
                                                <span aria-label='exclamation mark'> !</span> 
                                                <span aria-label='at sign'>@</span> 
                                                <span aria-label='hash'>#</span> 
                                                <span aria-label='dollar sign'>$</span> 
                                                <span aria-label='percent sign'>%</span>
                </p>

                
                <button disabled={!validName || !validPassword ? true : false}>
                    Sign In
                </button>
            </form>
            <p className='bluetext'>Don't have an account? <br/> 
                <span className='line'>
                    <a onClick={handleRegister}>Sign Up!</a>
                </span>
            </p>
            </section>
            </div>
        )}



export default Login;