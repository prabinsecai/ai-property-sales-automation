# AI agent

Phase 2 separates provider access (`app/llm.py`), query understanding, grounded retrieval,
and response validation. `LLM_MODE=mock` is deterministic and requires no network or paid API.
OpenAI-compatible and Anthropic-compatible modes fail clearly when their API key is absent.
Answers include property source references; unsupported guarantee/legal requests create an
escalation instead of being answered as facts.
