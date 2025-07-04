import React from 'react';
import { useLocation } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import './errorpage.css';

const ErrorPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { state } = location;

    const errorCode = state?.code || 'Unknown Error';
    const errorMessage = state?.message || 'An unexpected error occurred.';

    return (
        <div className="error-page">
            <h1>Error {errorCode}</h1>
            <p>{errorMessage}</p>
            <a onClick={() => navigate('/homepage')} className="home-link">Go back to Home</a>
        </div>
    );
};

export default ErrorPage;
