import apiClient from "./client.js";

export async function fetchFileStats() {
  const { data } = await apiClient.get("/files/stats/");
  return data;
}

export async function bulkDeleteFiles(count) {
  const { data } = await apiClient.post("/files/bulk-delete/", { count });
  return data;
}

export async function fetchTripFileStats(tripId) {
  const { data } = await apiClient.get(`/trips/${tripId}/files/stats/`);
  return data;
}

export async function deleteTripFiles(tripId) {
  const { data } = await apiClient.post(`/trips/${tripId}/files/delete/`);
  return data;
}
