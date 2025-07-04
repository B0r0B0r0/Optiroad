import React, { useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'
import useAuth from '../hooks/useAuth'
import useAxiosPrivate from '../hooks/useAxiosPrivate'
import useRefreshToken from '../hooks/useRefreshToken'

export default function PersistLogin() {

    const refresh = useRefreshToken()
    const { accessToken, setUser } = useAuth()
    const [loading, setLoading] = useState(true)
    const axiosPrivate = useAxiosPrivate()

    useEffect(() => {
        let isMounted = true

        async function verifyUser() {
            try {
                console.log("🔄 Încep cererea de refresh...");
                const { accessToken, csrfToken } = await refresh();
                console.log("✅ Refresh Token primit:", accessToken);
                console.log("✅ CSRF Token primit:", csrfToken);

                const { data } = await axiosPrivate.get("/api/user");
                console.log("✅ Date user:", data);
                setUser(data);
            } catch (error) {
                console.log("❌ Eroare în PersistLogin:", error.response);
            } finally {
                if (isMounted) setLoading(false);
            }
        }

        !accessToken ? verifyUser() : setLoading(false)

        return () => {
            isMounted = false
        }
    }, [])

    return (
        loading ? "Loading" : <Outlet />
    )
}