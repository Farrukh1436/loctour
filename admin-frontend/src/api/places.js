import apiClient from "./client.js";

export async function fetchPlaces(params = {}) {
  const { data } = await apiClient.get("/places/", { params });
  return data;
}

export async function createPlace(payload) {
  const { data } = await apiClient.post("/places/", payload);
  return data;
}

export async function updatePlace(id, payload) {
  const { data } = await apiClient.patch(`/places/${id}/`, payload);
  return data;
}

export async function uploadPlacePhoto(payload) {
  const formData = new FormData();
  Object.entries(payload).forEach(([key, value]) => formData.append(key, value));
  const { data } = await apiClient.post("/place-photos/", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
}
