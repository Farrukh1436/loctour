import apiClient from "./client.js";

export async function fetchExpenses(params = {}) {
  const { data } = await apiClient.get("/expenses/", { params });
  return data;
}

export async function createExpense(payload) {
  const { data } = await apiClient.post("/expenses/", payload);
  return data;
}
