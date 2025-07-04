import { axiosInstance } from "../axios/axios";
import useAuth from "./useAuth";

export default function useRefreshToken() {
    const { setAccessToken, setCSRFToken } = useAuth()

    function getCSRFToken() {
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            let [name, value] = cookie.split("=");
            if (name === "csrf_token") {
                return value;
            }
        }
        return null;
    }

    const refresh = async () => {
        const csrfToken = getCSRFToken();
        
        const response = await axiosInstance.post("/refresh", {}, {
            withCredentials: true,
            headers: { "X-CSRF-Token": csrfToken }  
        });
        setAccessToken(response.data.access_token)
        setCSRFToken(response.headers["x-csrf-token"])

        return { accessToken: response.data.access_token, csrfToken: response.headers["x-csrf-token"] }
    }

    return refresh
}