import { useContext, useDebugValue } from "react";
import AuthContext from "../context/AuthContext"

export default function useAuth() {
    return useContext(AuthContext)
}