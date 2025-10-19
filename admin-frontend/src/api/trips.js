import apiClient from "./client.js";

export async function fetchTrips(params = {}) {
  const { data } = await apiClient.get("/trips/", { params });
  return data;
}

export async function fetchTrip(id) {
  const { data } = await apiClient.get(`/trips/${id}/`);
  return data;
}

export async function createTrip(payload) {
  const { data } = await apiClient.post("/trips/", payload);
  return data;
}

export async function updateTrip(id, payload) {
  const { data } = await apiClient.patch(`/trips/${id}/`, payload);
  return data;
}

export async function fetchTripParticipants(id) {
  const { data } = await apiClient.get(`/trips/${id}/participants/`);
  return data;
}

export async function toggleTripAnnouncement(id) {
  const { data } = await apiClient.post(`/trips/${id}/toggle-announcement/`);
  return data;
}
