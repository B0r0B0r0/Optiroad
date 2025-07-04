import axios from "axios";

export const axiosInstance = axios.create({
    withCredentials: true, 
    headers: {
        "Content-Type": "application/json"
    }
});

export const axiosPrivateInstance = axios.create({
    withCredentials: true,
    headers: {
        "Content-Type": "application/json"
    }
});