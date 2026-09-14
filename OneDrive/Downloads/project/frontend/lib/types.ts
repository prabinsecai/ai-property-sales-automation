export type Property = {
  id: number; property_id: string; title: string; description: string; city: string; suburb: string;
  address: string; state: string; property_type: string; price: number; weekly_rent: number;
  bedrooms: number; bathrooms: number; parking: number; pet_policy: string; lease_duration: string;
  nearby_facilities: string[]; area_sqft: number; year_built: number; amenities: string[];
  image_url: string | null; is_available: boolean; availability_status: string; available_date: string | null;
  created_at: string; updated_at: string;
};
export type PropertyList = { items: Property[]; total: number; page: number; page_size: number };
export type SearchResult = { property: Property; score: number; match_type: string };
export type SearchResponse = { results: SearchResult[]; total: number; query?: string; interpreted_filters?: Record<string, unknown> };
export type Lead = { id: number; conversation_id?: string; name?: string; email?: string; phone?: string; intent?: string; budget?: number; preferences?: Record<string, unknown>; score: number; score_reasons: string[]; created_at: string; updated_at: string };
export type Escalation = { id: number; conversation_id: string; reason: string; message: string; status: string; created_at: string };
export type ChatResponse = { conversation_id: string; message: string; intent: string; confidence: number; source_references: { source_id: string; title?: string; excerpt?: string }[]; lead_id?: number; escalation_id?: number; lead_detected: boolean; escalation_required: boolean };
