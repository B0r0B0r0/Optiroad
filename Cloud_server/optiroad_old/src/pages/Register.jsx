import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInfoCircle, faCheck, faTimes, faHome } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import './register.css';
import video from '../multimedia/cars3.mp4';



const user_regex = /^[a-zA-Z][a-zA-Z0-9-_]{3,20}$/;
const password_regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$/;
const key_regex = /^[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}$/;
const email_regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;



const Register = () => {

    const navigate = useNavigate(); 

    const userRef = useRef();
    const errRef = useRef();

    const [user, setUser] = useState('');
    const [validName, setValidName] = useState(false);  
    const [userFocus, setUserFocus] = useState(false);

    const [email, setEmail] = useState('');
    const [validEmail, setValidEmail] = useState(false);
    const [emailFocus, setEmailFocus] = useState(false);

    const [password, setPassword] = useState('');
    const [validPassword, setValidPassword] = useState(false);
    const [passwordFocus, setPasswordFocus] = useState(false);

    const [confirmPassword, setConfirmPassword] = useState('');
    const [validConfirmPassword, setValidConfirmPassword] = useState(false);
    const [confirmPasswordFocus, setConfirmPasswordFocus] = useState(false);

    const [key, setKey] = useState('');
    const [validKey, setValidKey] = useState(false);
    const [keyFocus, setKeyFocus] = useState(false);

    const [errMsg, setErrMsg] = useState('');
    const [success, setSuccess] = useState(false);

    const formatKey = (value) => {
        value = value.replace(/[^a-zA-Z0-9]/g, '');
        value = value.slice(0, 16);
        return value.match(/.{1,4}/g)?.join('-') || value;
    };
    

    const handleKeyChange = (e) => {
        const formattedKey = formatKey(e.target.value);
        setKey(formattedKey);
    };

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
        const match = password === confirmPassword;
        setValidConfirmPassword(match);
    }, [password, confirmPassword]);

    useEffect(() => {
        const result = key_regex.test(key);
        setValidKey(result);
    }, [key]);

    useEffect(() => {
        setErrMsg('');
    }, [user,password,confirmPassword,key]);

    useEffect(() => {
        const result = email_regex.test(email);
        setValidEmail(result);
    }, [email]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const v1 = user_regex.test(user);
        const v2 = password_regex.test(password);
        const v3 = password === confirmPassword;
        const v4 = key_regex.test(key);
        const v5 = email_regex.test(email);
        if (!v1 || !v2 || !v3 || !v4 || !v5) {
            setErrMsg('Invalid Entry');
            return;
        }

        try {
            const response = await axios.post('/register', {
                username: user,
                password,
                key,
                email
            });

            if (response.status === 200) {
                navigate('/homepage');  
            }
        } catch (error) {
            console.error('There was an error!', error);
            navigate('/error', {
                state: {
                    code: error.response?.status || 500,
                    message: error.response?.data?.message || 'Internal Server Error'
                }
            });
        }

    }

    const handleLogin = () => {
        navigate('/login');
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
            <h1>Register</h1>
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
                    4 to 24 characters. <br/>
                    Must start with a letter. <br/>
                    Letters, numbers, hyphens, and underscores only.
                </p>

                <label htmlFor='email'> Email: 
                    <span className={validEmail ? 'valid' : 'hide'}>
                        <FontAwesomeIcon icon={faCheck} />
                    </span>
                    <span className={validEmail || !email ? 'hide' : 'invalid'}>
                        <FontAwesomeIcon icon={faTimes} />
                    </span>
                </label>
                <input
                    type='text'
                    id='email'
                    ref={userRef}
                    autoComplete='off'
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    aria-invalid={!validEmail}
                    aria-describedby='uidnote'
                    onFocus={() => setEmailFocus(true)}
                    onBlur={() => setEmailFocus(false)}
                />
                <p id='uidnote' className={ email && !validEmail ? 'instructions' : 'offscreen'}>
                    <FontAwesomeIcon icon={faInfoCircle} />
                    Between 5 to 50 characters. <br/>
                    Must contain a valid email format (e.g., username@domain.com). <br/>
                    Letters, numbers, dots (.), and underscores (_) allowed before the "@" symbol. <br/>
                    Valid domain names only (e.g., gmail.com, example.org).
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
                    8 to 24 characters. <br/>
                    At least one uppercase letter, one lowercase letter, one number, and one special character.<br/>
                    Allowed special characters: <span aria-label='exclamation mark'>!</span> 
                                                <span aria-label='at sign'>@</span> 
                                                <span aria-label='hash'>#</span> 
                                                <span aria-label='dollar sign'>$</span> 
                                                <span aria-label='percent sign'>%</span>
                </p>

                <label htmlFor='confirmpassword'>
                    Confirm Password:
                    <span className={validConfirmPassword && confirmPassword ? 'valid' : 'hide'}>
                        <FontAwesomeIcon icon={faCheck} />
                    </span>
                    <span className={validConfirmPassword || !confirmPassword ? 'hide' : 'invalid'}>
                        <FontAwesomeIcon icon={faTimes} />
                    </span>
                </label>
                <input 
                type='password'
                id='confirmpassword'
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                aria-invalid={!validConfirmPassword}
                aria-describedby='confirmpasswordnote'
                onFocus={() => setConfirmPasswordFocus(true)}
                onBlur={() => setConfirmPasswordFocus(false)}
                />
                <p id='confirmpasswordnote' className={!validConfirmPassword && confirmPassword ? 'instructions' : 'offscreen'}>
                    <FontAwesomeIcon icon={faInfoCircle} />
                    Must match the password above.
                </p>
                <p ref={errRef} className={errMsg ? "errmsg" : "offscreen"} aria-live="assertive"> {errMsg} </p>   

                <label htmlFor='key'> Registration Key: 
                    <span className={validKey ? 'valid' : 'hide'}>
                        <FontAwesomeIcon icon={faCheck} />
                    </span>
                    <span className={validKey || !key ? 'hide' : 'invalid'}>
                        <FontAwesomeIcon icon={faTimes} />
                    </span>
                </label>
                <input
                    type='text'
                    id='key'
                    ref={userRef}
                    autoComplete='off'
                    onChange={handleKeyChange}
                    required
                    value={key}
                    aria-invalid={!validName}
                    aria-describedby='keynote'
                    onFocus={() => setKeyFocus(true)}
                    onBlur={() => setKeyFocus(false)}
                />
                <p id='keynote' className={ key && !validKey ? 'instructions' : 'offscreen'}>
                    <FontAwesomeIcon icon={faInfoCircle} />
                    You must enter the key provided to you by the administrator. <br/>
                    If you do not posses such a key, please contact the administration. <br/>
                    The key is in the format: XXXX-XXXX-XXXX-XXXX
                </p>
                <button disabled={!validName || !validPassword || !validConfirmPassword || !validKey ? true : false}>
                    Sign Up
                </button>
            </form>
            <p className='bluetext'>
                Already have an account? <br/> 
                <span className='line'>
                    <a onClick={handleLogin} >Sign In!</a>
                </span>
            </p>
            </section>
            </div>
        )}


export default Register;