import apiClient from "./client.js";

export async function fetchUserTrips(params = {}) {
  const { data } = await apiClient.get("/user-trips/", { params });
  return data;
}

export async function updateUserTrip(id, payload) {
  const { data } = await apiClient.patch(`/user-trips/${id}/`, payload);
  return data;
}
