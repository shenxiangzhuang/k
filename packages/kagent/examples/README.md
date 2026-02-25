# kagent examples

Eight self-contained scripts organized into three groups.
Read them in order — each builds on the concepts of the previous one.

## Prerequisites

```bash
export DEEPSEEK_API_KEY="sk-..."
cd <repo-root>
uv sync
```

## Examples

### Basics — Getting started with `Agent`

| File | What it shows |
|------|---------------|
| [`basics/01_quickstart.py`](basics/01_quickstart.py) | Create an agent with tools, one-shot `complete()` |
| [`basics/02_multi_tool_agent.py`](basics/02_multi_tool_agent.py) | Non-streaming & streaming, multi-tool, multi-turn, steer/abort |

### Advanced — Lower-level APIs & context management

| File | Level | What it shows |
|------|-------|---------------|
| [`advanced/03_agent_loop.py`](advanced/03_agent_loop.py) | 1 — `agent_loop` | Custom `context_builder`, `should_continue`, `on_tool_result` |
| [`advanced/04_agent_step.py`](advanced/04_agent_step.py) | 0 — `agent_step` | Single-step primitive; you own the loop and state |
| [`advanced/05_context_builders.py`](advanced/05_context_builders.py) | 1–2 | Built-in context builders: sliding window, compaction, adaptive |

### Observability — Logging, hooks & tracing

| File | What it shows |
|------|---------------|
| [`observability/06_logging.py`](observability/06_logging.py) | stdlib logging for kai and kagent internals |
| [`observability/07_hooks.py`](observability/07_hooks.py) | LoggingHooks, custom Hooks subclass, MultiHooks |
| [`observability/08_trace.py`](observability/08_trace.py) | OTelHooks — OpenTelemetry tracing with Jaeger export |

## Running

```bash
uv run python packages/kagent/examples/basics/01_quickstart.py
uv run python packages/kagent/examples/observability/08_trace.py
# … and so on
```

## The three levels at a glance

```
Level 2 — Agent          stateful SDK, interactive control (steer / abort / follow_up)
  └─ Level 1 — agent_loop    multi-turn loop, plain-function callbacks
       └─ Level 0 — agent_step    one LLM call + tool execution, you manage state
```

Pick the lowest level that gives you the control you need.
Most applications start at **Level 2** and drop down only when required.

## Tool definition pattern

```python
from pydantic import BaseModel, Field
from kai import Tool, ToolResult

class MyTool(Tool):
    name: str = "my_tool"
    description: str = "What this tool does."

    class Params(BaseModel):
        query: str = Field(description="The input query")

    async def execute(self, params: "MyTool.Params") -> ToolResult:
        return ToolResult(output=f"result for {params.query}")
```

JSON Schema is auto-generated from `Params` — no manual `parameters` dict needed.
