import axiosInstance from "./axiosInstance";

export const registerUser = async (credentials) => {
  try {
    const response = await axiosInstance.post("/register", credentials);
    return response.data; 
  } catch (error) {
    throw error.response?.data?.message || "Registration failed. Please try again.";
  }
};

export const loginUser = async (credentials) => {
  try {
    const response = await axiosInstance.post("/login", credentials);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.message || "Invalid credentials");
    }
};

export const refreshAccessToken = async () => {
  try {
    await axiosInstance.post("/refresh", {}, { withCredentials: true });
    return true;
  } catch (error) {
    console.error("Error refreshing token:", error);
    return false;
  }
};

export const logoutUser = async () => {
  try {
    await axiosInstance.post("/logout");
  } catch (error) {
    console.error("Logout error:", error);
  }
};

export const refreshCSRFToken = async () => {
  try {
    const response = await axiosInstance.get("/csrf-token");
    const csrfToken = response.data.csrfToken;
    return csrfToken;
  } catch (error) {
    console.error("Error refreshing CSRF token:", error);
  }
}


export const changePassword = async ({ oldPassword, newPassword }) => {
  try {
    const response = await axiosInstance.post("/change-password", {
      old_password: oldPassword,
      new_password: newPassword
    });
    return response.data;
  } catch (error) {
    const msg = error.response?.data?.message || "Password change failed";
    throw new Error(msg);
  }
};

export const sendRequestKey = async (formData) => {
    const formDataObj = new FormData();
    Object.keys(formData).forEach((key) => {
      formDataObj.append(key, formData[key]);
    });
  
    const response = await axiosInstance.post("/add-user", formDataObj, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  
    return response.data;
  };

export const getUserProfile = async () => {
  try {
    const response = await axiosInstance.get("/profile", {
      withCredentials: true, 
    });
    return response.data; 
  } catch (error) {
    console.error("Failed to fetch user profile:", error);
    throw new Error(error.response?.data?.message || "Could not retrieve user profile");
  }
};
