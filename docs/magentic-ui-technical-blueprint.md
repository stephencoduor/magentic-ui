# Magentic-UI Technical Blueprint

> A consolidated reference for understanding, extending, and operating the Magentic-UI multi-agent assistant.

---

## Table of Contents
- [Project Overview](#project-overview)
  - [Product Vision](#product-vision)
  - [Key Capabilities](#key-capabilities)
  - [Primary User Journeys](#primary-user-journeys)
- [System Architecture](#system-architecture)
  - [Component Layers](#component-layers)
  - [Runtime Workflow](#runtime-workflow)
  - [Technology Stack](#technology-stack)
  - [Cross-Cutting Concerns](#cross-cutting-concerns)
- [Repository & Folder Structure](#repository--folder-structure)
- [Frontend Codebase](#frontend-codebase)
  - [UI Composition](#ui-composition)
  - [State Management & Configuration](#state-management--configuration)
  - [Data Flow & API Access](#data-flow--api-access)
- [Backend Codebase](#backend-codebase)
  - [FastAPI Service Layer](#fastapi-service-layer)
  - [Agent Orchestration](#agent-orchestration)
  - [Persistence & Background Services](#persistence--background-services)
- [Deployment, CI/CD & Docker](#deployment-cicd--docker)
  - [Local Development Profiles](#local-development-profiles)
  - [Container Images](#container-images)
  - [Automation Pipelines](#automation-pipelines)
- [Testing & Quality Gates](#testing--quality-gates)
- [Operational Playbooks](#operational-playbooks)
  - [Observability](#observability)
  - [Security Posture](#security-posture)
- [Roadmap & Implementation Plan](#roadmap--implementation-plan)
- [Appendix](#appendix)
  - [Glossary](#glossary)
  - [PDF Export Guide](#pdf-export-guide)
  - [Further Reading](#further-reading)

---

## Project Overview

### Product Vision
Magentic-UI is a research prototype that blends a human-centered interface with a cooperative multi-agent system. The platform enables end users to co-plan tasks, supervise autonomous browser agents, and iterate on generated code in real time. Built on top of AutoGen, it aims to maximize transparency and maintain human control while still benefiting from automation.

### Key Capabilities
- **Co-Planning:** Suggests structured plans, asks for approvals, and adapts based on user edits.
- **Co-Tasking:** Streams agent activity (including live browser playback) and invites user input when needed.
- **Action Guardrails:** Routes sensitive actions through configurable approval policies powered by dedicated guard models.
- **Plan Memory:** Learns from past sessions, supports retrieval of historical plans, and reuses them when helpful.
- **Multi-Modal Tooling:** Integrates browsing, code execution, file analysis, and MCP-compatible external tools.

### Primary User Journeys
1. **Task Automation Session:** A user launches Magentic-UI, configures agent autonomy, and monitors a web automation task with optional inline approvals.
2. **Research Experiment:** A researcher adjusts model backends and orchestrator configuration to benchmark new agent behaviors.
3. **Operational Monitoring:** An operator connects to the backend API to inspect session state, audit approvals, and download generated artifacts.

---

## System Architecture

### Component Layers
```
+---------------------+---------------------------------------------------+
| Layer               | Responsibilities                                 |
+=====================+===================================================+
| Frontend (Gatsby)   | SPA rendered UI, session timeline, configuration  |
|                     | panels, WebSocket client, and plan editor.        |
+---------------------+---------------------------------------------------+
| Backend (FastAPI)   | REST & WebSocket APIs, session/state management,  |
|                     | plan persistence, approval workflow, and storage. |
+---------------------+---------------------------------------------------+
| Agent Runtime       | AutoGen-based multi-agent teams (orchestrator,    |
|                     | web surfer, coder, file surfer, guard).           |
+---------------------+---------------------------------------------------+
| Execution Sandbox   | Dockerized Python environment for safe code       |
|                     | execution and file manipulation.                  |
+---------------------+---------------------------------------------------+
```

### Runtime Workflow
1. The user interacts with the Gatsby SPA, which communicates via REST for configuration and WebSockets for live session updates.
2. FastAPI routes requests through manager abstractions that initialize databases, orchestrate agent teams, and schedule browser automation.
3. Agent teams coordinate via AutoGen, negotiating plans, performing tool calls (e.g., Playwright-driven browsing), and streaming status back to the UI.
4. Generated artifacts are stored in run directories that are mounted inside Docker for deterministic execution.

### Technology Stack
| Dimension              | Technologies |
| ---------------------- | ------------ |
| Frontend               | React + Gatsby, TypeScript, TailwindCSS, Zustand, WebSockets |
| Backend                | FastAPI, Pydantic, SQLModel, async managers, Loguru |
| Agents & Automation    | AutoGen (agents, orchestration), Playwright browser automation |
| Build & Tooling        | `uv` package manager, `poethepoet` tasks, Pytest, Pyright |
| Packaging & Runtime    | Docker (multi-stage builds), GHCR images, Python 3.12 |

### Cross-Cutting Concerns
- **Configuration:** Centralized in `magentic_ui_config.py` with environment overrides for Docker vs. local execution.
- **Security:** Approval guard enforces policies for sensitive actions and isolates code execution inside dedicated containers.
- **Performance:** Web-surfer agent supports headless mode and loop-only team configuration for streamlined automation.
- **Extensibility:** MCP agents, model provider abstraction, and plugin-style tool registration enable rapid capability growth.

---

## Repository & Folder Structure
| Path | Description |
| ---- | ----------- |
| `frontend/` | Gatsby SPA with UI components, settings panels, and client-side state management. |
| `src/magentic_ui/backend/` | FastAPI app, data models, CLI entry points, and orchestration managers. |
| `src/magentic_ui/agents/` | AutoGen agent implementations including web surfer, coder, and MCP integrations. |
| `src/magentic_ui/tools/` | Tooling wrappers (Playwright browsers, file utilities) exposed to agents. |
| `docker/` | Container definitions for the UI browser environment and Python execution sandbox. |
| `experiments/` | Benchmark harnesses and evaluation scripts for GAIA, AssistantBench, etc. |
| `tests/` | Automated unit and integration tests spanning backend services and agent logic. |
| `docs/` | Project documentation, diagrams, and (now) this technical blueprint. |

---

## Frontend Codebase

### UI Composition
The UI is composed of reusable layout primitives (`components/layout.tsx`) combined with feature-specific panels housed under `components/features`. Styling is driven by TailwindCSS, while Gatsby configures routing and static asset generation.

### State Management & Configuration
Zustand powers the global configuration store for agent behavior, exposing helper utilities for generating YAML-based overrides that mirror backend expectations.

```tsx title="frontend/src/components/store.tsx"
export const useSettingsStore = create<SettingsState>()((set) => ({
  config: defaultConfig,
  updateConfig: (update) =>
    set((state) => ({
      config: { ...state.config, ...update },
    })),
  resetToDefaults: () => set({ config: defaultConfig }),
}));
```
*Source: `frontend/src/components/store.tsx`*

The store synchronizes user-selected defaults (e.g., approval policies, model providers) and emits serialized configuration via helper functions such as `generateOpenAIModelConfig` for quick copy/paste into YAML configs.

### Data Flow & API Access
- **REST:** Gatsby pages call the `/api` namespace exposed by FastAPI for sessions, plans, settings, and validation.
- **WebSockets:** Real-time status updates stream through `/api/ws`, enabling live session progress and browser playback.
- **Authentication:** The open-source build relies on API keys configured in the backend; enterprise deployments can extend `signin.tsx` for custom auth flows.

---

## Backend Codebase

### FastAPI Service Layer
The backend mounts a FastAPI application with a dedicated lifespan manager that orchestrates configuration loading, manager initialization, and cleanup.

```python title="src/magentic_ui/backend/web/app.py"
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        config: dict[str, Any] = {}
        config_file = os.environ.get("_CONFIG")
        if config_file:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
        await init_managers(
            initializer.database_uri,
            initializer.config_dir,
            initializer.app_root,
            os.environ["INTERNAL_WORKSPACE_ROOT"],
            os.environ["EXTERNAL_WORKSPACE_ROOT"],
            os.environ["INSIDE_DOCKER"] == "1",
            config,
            os.environ["RUN_WITHOUT_DOCKER"] == "True",
        )
    finally:
        ...
```
*Source: `src/magentic_ui/backend/web/app.py`*

Routers under `routes/` expose domain-specific endpoints for sessions, runs, plan management, settings, and health checks. Static assets are mounted alongside the API to serve the compiled frontend and session artifacts.

### Agent Orchestration
Agent team composition is centralized in `task_team.py`, enabling dynamic assembly of orchestrator, web surfer, coder, and guard agents based on runtime configuration.

```python title="src/magentic_ui/task_team.py"
if magentic_ui_config.user_proxy_type in ["dummy", "metadata"]:
    model_client_action_guard = get_model_client(
        magentic_ui_config.model_client_configs.action_guard,
        is_action_guard=True,
    )
    approval_guard = ApprovalGuard(
        input_func=always_yes_input,
        default_approval=False,
        model_client=model_client_action_guard,
        config=ApprovalConfig(
            approval_policy=approval_policy,
        ),
    )
with ApprovalGuardContext.populate_context(approval_guard):
    web_surfer = WebSurfer.from_config(websurfer_config)
```
*Source: `src/magentic_ui/task_team.py`*

The orchestrator coordinates turn-taking via group chats, leverages Playwright browser resources, and enforces approval guardrails for sensitive operations.

### Persistence & Background Services
- **Database:** SQLModel-backed storage initialized through `backend/database` manages session metadata and agent runs.
- **File System:** Run directories mirror session IDs, allowing artifact download via the `/files` mount.
- **Managers:** Initialization routines (database, connection pooling, team registry) live under `backend/teammanager` and `backend/utils` for reuse across CLI and API entry points.

---

## Deployment, CI/CD & Docker

### Local Development Profiles
- **Standard Mode:** `magentic-ui --port 8081` launches the UI with Dockerized execution agents.
- **Non-Docker Mode:** `magentic-ui --run-without-docker` skips sandboxed execution for limited environments.
- **CLI Mode:** `magentic-cli` provides a terminal-first experience for batch operations.

### Container Images
Two first-party container images ship with the repository:
1. **Browser Environment:** Provides a hardened Chromium + VNC runtime for the web-surfer agent.
2. **Python Execution Environment:** Multi-stage Dockerfile installs dependencies, configures a virtualenv, and sets execution entrypoints.

```dockerfile title="docker/magentic-ui-python-env/Dockerfile"
FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    ffmpeg \
    exiftool
RUN python -m venv /opt/venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
*Source: `docker/magentic-ui-python-env/Dockerfile`*

Both images are published to GitHub Container Registry (GHCR) and reused by the CLI and backend during task execution.

### Automation Pipelines
GitHub Actions orchestrate formatting, linting, type checking, tests, Docker publication, static site deployment, and CodeQL scanning.

```yaml title=".github/workflows/checks.yaml"
jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: astral-sh/setup-uv@v6
      - run: uv sync --all-extras
      - run: |
          source .venv/bin/activate
          poe fmt src --check
  lint:
    needs: format
    runs-on: ubuntu-latest
    steps:
      - run: |
          source .venv/bin/activate
          poe lint src
```
*Source: `.github/workflows/checks.yaml`*

Additional workflows cover Docker image build/push, CodeQL static analysis, and Gatsby site deployment to GitHub Pages.

---

## Testing & Quality Gates
- **Formatting:** Enforced via `poe fmt` tasks over `src/`, `samples/`, and `tests/`.
- **Static Analysis:** Pyright validates backend typing; ESLint/TSC run through Gatsby during frontend builds.
- **Unit & Integration Tests:** Pytest suites cover backend services, agent orchestration, and tool integration.
- **Coverage Reporting:** Coverage artifacts are uploaded on CI and ready for Codecov integration when tokens are provided.

---

## Operational Playbooks

### Observability
- **Logging:** Loguru captures structured logs across backend services. Configure sinks via environment variables for production deployments.
- **Metrics:** FastAPI can be paired with Prometheus exporters; extend `backend/web/app.py` to expose `/metrics` endpoints.
- **Tracing:** Integrate OpenTelemetry by wrapping agent tool calls and HTTP endpoints for distributed tracing across services.

### Security Posture
- **Secrets Management:** API keys (OpenAI, Azure, Ollama) are sourced from environment variables or config files loaded during lifespan initialization.
- **Sandboxing:** All execution happens within isolated Docker containers, preventing host-level side effects.
- **Approval Guard:** Policies (`always`, `never`, `auto-conservative`, `auto-permissive`) ensure human-in-the-loop validation for high-risk operations.

---

## Roadmap & Implementation Plan
1. **Improve Observability:** Add Prometheus instrumentation to key backend endpoints, integrate with Grafana dashboards.
2. **Session Replay Enhancements:** Persist Playwright traces for post-run playback and debugging.
3. **Pluggable Auth:** Provide optional OAuth/OpenID Connect integration for enterprise deployments.
4. **Frontend Performance:** Adopt React Server Components or streaming APIs to accelerate initial page loads.

| Phase | Focus | Key Tasks |
| ----- | ----- | --------- |
| Foundation | Telemetry & Reliability | Instrument metrics, add structured tracing, tighten log schemas. |
| Enablement | Developer Experience | Expand CLI ergonomics, document environment variables, bundle sample configs. |
| Expansion | Enterprise Features | Integrate auth, audit logging, and customizable approval workflows. |

---

## Appendix

### Glossary
- **Agent:** An AutoGen-driven component with specialized skills (e.g., web navigation, coding).
- **Approval Guard:** Policy enforcement layer that mediates sensitive tool invocations.
- **Run Directory:** Workspace folder containing artifacts, logs, and browser traces for a session.
- **MCP:** Model Context Protocol servers that extend tool availability for the agent team.

### PDF Export Guide

Generate a polished PDF copy of this blueprint on demand rather than tracking binary artifacts in the repository:

```bash
python scripts/export_markdown_to_pdf.py docs/magentic-ui-technical-blueprint.md
```

The script renders the Markdown with the same styling used for the canonical `docs` site output and will place the exported PDF alongside the source file. Git ignores `docs/*.pdf`, so contributors should regenerate the artifact locally whenever a refreshed copy is required.

### Further Reading
- [README](../README.md)
- [Backend README](../src/magentic_ui/backend/README.md)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)
- [Experiments](../experiments/README.md)
- PDF Export Script: `python scripts/export_markdown_to_pdf.py docs/magentic-ui-technical-blueprint.md`

