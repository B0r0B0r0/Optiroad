import axiosInstance from "./axiosInstance";

export const addCity = async ({ country, county, city }) => {
  try {
    const response = await axiosInstance.post("/cities/add", {
      country,
      county,
      city
    });
    return response.data;
  } catch (error) {
    const msg = error.response?.data?.message || "Unknown error";
    return { error: msg };
  }
};

export const getMyCities = async () => {
  try {
    const response = await axiosInstance.get("/cities/get-cities");
    return response.data;
  } catch (error) {
    return [];
  }
};

export const getCityCoordinates = async ({ country, county, city }) => {
  try {
    const response = await axiosInstance.post("/cities/coordinates", {
      country,
      county,
      city
    });
    return response.data;
  } catch (error) {
    const msg = error.response?.data?.message || "Unknown error";
    return { error: msg };
  }
};


export const getCityDevices = async ({ country, county, city }) => {
  try {
    const response = await axiosInstance.post("/cities/devices", {
      country,
      county,
      city
    });
    return response.data.devices || [];
  } catch (error) {
    const msg = error.response?.data?.message || "Unknown error";
    return { error: msg };
  }
};