import axiosInstance from "./axiosInstance";

export const getPendingUsers = async () => {
  try {
    const response = await axiosInstance.get("/pending-users");
    return response.data || [];
  } catch (error) {
    console.error("Eroare la obținerea utilizatorilor pending:", error);
    throw error;
  }
};

export const denyUser = async (userId, id_front, id_back, fname, lname, email) => {
  try {
    const response = await axiosInstance.post(`/deny-user`,
       {
         user_id: userId, 
         id_front, 
         id_back,
         fname,
         lname,
         email
       });
    return response.data;
  } catch (error) {
    console.error("Eroare la respingerea utilizatorului:", error);
    return error;
  }
};

export const approveUser = async(user_id, fname, lname, email) => {
  try {
    const response = await axiosInstance.post(`/approve-user`, {
      user_id,
      fname,
      lname,
      email
    });
    return response.data;
  } catch (error) {
    console.error("Eroare la aprobarea utilizatorului:", error);
    return error;
  }
}