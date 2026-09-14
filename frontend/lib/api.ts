import type { ChatResponse, Escalation, Lead, Property, PropertyList, SearchResponse } from "./types";
const base = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base}${path}`, { ...init, headers: { "Content-Type": "application/json", ...init?.headers }, cache: "no-store" });
  if (!response.ok) { const body = await response.text(); throw new Error(body || `Request failed (${response.status})`); }
  return response.json();
}
export const api = {
  listProperties: (params: URLSearchParams) => request<PropertyList>(`/properties?${params}`),
  getProperty: (id: string) => request<Property>(`/properties/${encodeURIComponent(id)}`),
  search: (body: Record<string, unknown>) => request<SearchResponse>("/properties/search", { method: "POST", body: JSON.stringify(body) }),
  chat: (message: string, conversation_id?: string) => request<ChatResponse>("/chat", { method: "POST", body: JSON.stringify({ message, conversation_id }) }),
  leads: () => request<Lead[]>("/leads"),
  lead: (id: string) => request<Lead>(`/leads/${id}`),
  escalations: () => request<Escalation[]>("/escalations"),
  escalation: (id: string) => request<Escalation>(`/escalations/${id}`)
};
