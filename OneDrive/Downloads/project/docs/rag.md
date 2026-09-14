# Retrieval augmented search

`POST /knowledge/reindex` builds one document per property and upserts deterministic or
OpenAI embeddings into Chroma. `POST /knowledge/search` embeds only the query, performs
Chroma nearest-neighbor retrieval, then hydrates results by metadata `property_id`.

Retrieval is not a guarantee of truth: stale data, weak matches, or embedding ambiguity can
produce incomplete results or hallucinated interpretations. Consumers should treat database
fields as authoritative and use structured filters where precision matters.
