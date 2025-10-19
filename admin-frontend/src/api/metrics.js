import apiClient from "./client.js";

export async function fetchOverview(range = "30") {
  const { data } = await apiClient.get("/metrics/overview/", {
    params: { range: `${range}d` }
  });
  return data;
}
