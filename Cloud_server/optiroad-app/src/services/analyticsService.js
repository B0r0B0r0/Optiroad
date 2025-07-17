import axiosInstance from "./axiosInstance";

export const getAnalyticsData = async ({ country, county, city }) => {
  try {
    const response = await axiosInstance.post(
      `/cities/get-analytics`,
      { city, county, country },
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching analytics data:", error);
    throw error;
  }
};