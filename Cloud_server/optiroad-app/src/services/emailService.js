import axiosInstance from "./axiosInstance";

export const sendContactEmail = async (formData) => {
  const response = await axiosInstance.post("/contact-mail", formData);
  return response.data;
};

