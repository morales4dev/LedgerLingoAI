# Python

## Layer 1 — generic small Python

- Type hints on new and changed public functions.
- Pydantic at **non-LLM** Python boundaries (config objects, parsed JSON after you already have a string, future non-LLM APIs). Pattern only: do not add `pydantic` to `backend/requirements.txt` in an OS-only change. First product import pins it.
- Do not invent APIs, SDK methods, or library behavior. If it is not in the pin or Context7, do not guess.
- SOLID, DRY, PEP 8.
- Named errors; do not swallow with bare `except`.
- Validate input at boundaries.
- Structured logs (event + fields), not ad-hoc print for new operational logging.
- Early return; keep the happy path unindented.
- Secrets stay in env (`.env` gitignored). Names only in `.env.example`. Never commit secrets.

## Layer 2 — Twin stack

- Layout: app under `backend/src/`, venv `backend/.venv`, install with uv.
- Create the venv with `uv venv`. Install packages with `uv pip install --python backend/.venv/bin/python`. Never bare `pip install`.
- Pin only direct runtime deps in `backend/requirements.txt`. Do not pin unused transitives (fastapi, uvicorn, httpx). Do not add unpinned agent SDKs.
- Runtime: Python 3.12.12 (documented; not a pip pin).
- App: Gradio `ChatInterface` under `backend/src/`.
- Model client: MiniMax-M2.5 via the **sync** OpenAI-compatible `OpenAI()` client (`openai`). Chat stays sync. Do not document or rewrite the loop as async.
- Current runtime pins:

```
gradio==6.26.0
openai==3.8.0
pypdf==6.17.0
python-dotenv==1.2.3
requests==2.34.2
```

- Do not change visitor-facing chat or migrate `backend/src/**` unless a product change says so.

## LLM protocol (targets only)

These are coding targets for a later **product** change. Do not implement them in `backend/src/**` in an OS-only change.

- Structured model output: put `model_json_schema()` in the prompt, parse JSON in Python, then `model_validate`. Do not trust `output_type` / constrained decoding as validation.
- Tools: typed function + docstring + SDK decorator. Do not migrate week-1 hand-written tool JSON until a product change says so.
