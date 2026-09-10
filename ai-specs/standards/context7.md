# Context7

Resolve the correct library ID, then query with the pinned package version. Do not guess IDs. Do not pin a hosted MCP server URL. Do not add `.vscode/mcp.json`.

Resolved IDs (apply-time resolve pass):

| Package | Pin | Context7 ID |
| --- | --- | --- |
| gradio | 6.26.0 | `/gradio-app/gradio` |
| openai | 3.8.0 | `/openai/openai-python` |
| pytest | 9.1.1 | `/pytest-dev/pytest` |
| playwright | 1.62.0 | `/microsoft/playwright-python` |

Pass the pin as the version when the tool accepts one. If a version string is missing from Context7, still use the ID above and name the pin in the query.
