# Leads

Contact and qualification entities are extracted during chat and upserted by conversation.
`POST /leads` and `GET /leads` expose the records. Scores are transparent (email 35, phone 20,
budget 25, intent 20) and include `score_reasons`.
