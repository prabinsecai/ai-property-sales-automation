# Conversations

`POST /chat` accepts a message and optional `conversation_id`. Conversations, messages, and
retrieval traces are persisted in SQLite. Reuse the returned ID to retain memory, and retrieve
the transcript with `GET /conversations/{conversation_id}/messages`.
