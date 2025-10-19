import apiClient from "./client.js";

export async function fetchTravelers(params = {}) {
  const { data } = await apiClient.get("/travelers/", { params });
  return data;
}

export async function updateTraveler(id, payload) {
  const { data } = await apiClient.patch(`/travelers/${id}/`, payload);
  return data;
}
