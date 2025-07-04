import React from 'react';
import { useNavigate } from 'react-router-dom';
import './homepage.css';
import video from '../multimedia/cars3.mp4';

const Homepage = () => {

    const navigate = useNavigate();

    const redirectToRegister = () => {
        navigate('/register');
    };

    const redirectToLogin = () => {
        navigate('/login');
    };

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
            <section className="homepage__content">
            <div className="background-overlay"></div>
            <div className="homepage__overlay">
                <div className="homepage__header">
                    <h1>Welcome to OptiRoad</h1>
                    <h2>Revolutionizing Traffic in Intelligent Cities</h2>
                </div>
                <div className="homepage__content">
                    <p className="homepage__text">
                        At OptiRoad, we leverage cutting-edge technology to create smarter traffic solutions for modern cities. 
                        Join us in transforming urban mobility and making cities more efficient and enjoyable to live in.
                    </p>
                    <p className="homepage__text">
                        You need to be logged in to access our services. Please contact an administrator for a registration key and make your city great today!
                    </p>
                    <div className="homepage__buttons">
                        <div className="button-group">
                            <p className='bluetext' >Make your city great today!</p>
                            <button className="button-register" onClick={redirectToRegister}>Register</button>
                        </div>
                        <div className="button-group">
                            <p className='bluetext'>If you already have an account</p>
                            <button className="button-login" onClick={redirectToLogin}>Login</button>
                        </div>
                    </div>
                    <p className="homepage__footer">
                        Together, we can build the future of urban mobility. Contact us today to learn more about our innovative solutions.
                    </p>
                </div>
            </div>
                <div className='bottom_group'>
                <div><a href='#' className='bluetext'>I would like to learn more about OptiRoad</a></div>
                <div><a href='#' className='bluetext'>I would like to contact an administrator!</a></div>
            </div>
            </section>
        </div>
    );
};

export default Homepage;
