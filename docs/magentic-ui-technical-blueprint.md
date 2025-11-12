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
  - [Technology Primer](#technology-primer)
  - [Routing & Page Composition](#routing--page-composition)
  - [Layout Shell & Global Context](#layout-shell--global-context)
  - [Session Lifecycle & Data Fetching](#session-lifecycle--data-fetching)
  - [Real-time Collaboration Flow](#real-time-collaboration-flow)
  - [Configuration & Feature Panels](#configuration--feature-panels)
  - [Page-to-Backend Interaction Map](#page-to-backend-interaction-map)
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

### Technology Primer
Magentic-UI’s frontend is a Gatsby Single Page Application (SPA) written in React and TypeScript. Styling comes from TailwindCSS utility classes, component theming from Ant Design, and lightweight global state from Zustand. If you are new to this stack, remember:

- **React components** describe UI using JSX (HTML-like syntax embedded inside TypeScript functions).
- **Gatsby pages** automatically become routes based on file name (e.g., `frontend/src/pages/index.tsx` renders at `/`).
- **Zustand stores** provide React hooks that expose global state without boilerplate reducers.
- **TailwindCSS classes** such as `flex` or `h-full` are concatenated strings that configure CSS layout and spacing.

### Routing & Page Composition
All user-facing routes live under `frontend/src/pages`. Gatsby injects data requested through GraphQL queries defined alongside each page. The entry route is intentionally minimal because the conversational UI is rendered via shared layout components.

```tsx
// Source: frontend/src/pages/index.tsx (lines 1-24)
const IndexPage = ({ data }: any) => {
  return (
    <MagenticUILayout meta={data.site.siteMetadata} title="Home" link={"/"}>
      <main style={{ height: "100%" }} className=" h-full ">
      </main>
    </MagenticUILayout>
  );
};
```

The `<MagenticUILayout>` component is shared by other Gatsby pages (sign-in, documentation) to guarantee consistent headers, theming, and sidebars.

### Layout Shell & Global Context
`frontend/src/components/layout.tsx` provides the global shell. It wires together application context (for user identity and dark mode) with the session manager that powers the chat workspace.

```tsx
// Source: frontend/src/components/layout.tsx (lines 23-108)
const MagenticUILayout = ({
  meta,
  title,
  link,
  showHeader = true,
  restricted = false,
  activeTab,
  onTabChange,
}: Props) => {
  const { darkMode, user, setUser } = React.useContext(appContext);
  const { sidebar } = useConfigStore();
  const { isExpanded } = sidebar;
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  React.useEffect(() => {
    if (!user?.email) {
      const defaultEmail = "default";
      setUser({ ...user, email: defaultEmail, name: defaultEmail });
      if (typeof window !== "undefined") {
        window.localStorage.setItem("user_email", defaultEmail);
      }
    }
  }, [user, setUser]);

  return (
    <div className="h-screen flex">
      <ConfigProvider theme={{ /* Tailwind-compatible design tokens */ }}>
        <main className="flex-1 p-1 text-primary" style={{ height: "100%" }}>
          <SessionManager />
        </main>
      </ConfigProvider>
    </div>
  );
};
```

Key takeaways for new React developers:

1. **Context providers** (`appContext`, `useConfigStore`) supply user/session state to all children.
2. **Side effects** in `useEffect` perform runtime adjustments such as auto-provisioning a default user or updating the `<html>` theme class.
3. **The shell does not fetch data directly**—that logic lives in feature components injected into the layout.

### Session Lifecycle & Data Fetching
`SessionManager` orchestrates session CRUD, selection, and sidebar interactions. It delegates persistence to the typed REST helpers in `frontend/src/components/views/api.ts`.

```tsx
// Source: frontend/src/components/views/api.ts (lines 15-59)
async listSessions(userId: string): Promise<Session[]> {
  const response = await fetch(
    `${this.getBaseUrl()}/sessions/?user_id=${userId}`,
    {
      headers: this.getHeaders(),
    }
  );
  const data = await response.json();
  if (!data.status)
    throw new Error(data.message || "Failed to fetch sessions");
  return data.data;
}

async createSession(
  sessionData: Partial<Session>,
  userId: string
): Promise<Session> {
  const session = {
    ...sessionData,
    user_id: userId,
  };

  const response = await fetch(`${this.getBaseUrl()}/sessions/`, {
    method: "POST",
    headers: this.getHeaders(),
    body: JSON.stringify(session),
  });
  const data = await response.json();
  if (!data.status)
    throw new Error(data.message || "Failed to create session");
  return data.data;
}
```

These helpers wrap fetch calls and enforce consistent headers. `SessionManager` consumes them to present loading spinners, optimistic updates, and URL synchronization:

```tsx
// Source: frontend/src/components/views/manager.tsx (lines 59-151)
const fetchSessions = useCallback(async () => {
  if (!user?.email) return;

  try {
    setIsLoading(true);
    const data = await sessionAPI.listSessions(user.email);
    setSessions(data);

    const params = new URLSearchParams(window.location.search);
    const sessionId = params.get("sessionId");
    if (!session && data.length > 0 && !sessionId) {
      setSession(data[0]);
    } else {
      if (data.length === 0) {
        createDefaultSession();
      }
    }
  } catch (error) {
    messageApi.error("Error loading sessions");
  } finally {
    setIsLoading(false);
  }
}, [user?.email, setSessions, session, setSession]);

const handleSaveSession = async (sessionData: Partial<Session>) => {
  if (!user || !user.email) return;

  try {
    setIsLoading(true);
    if (sessionData.id) {
      const updated = await sessionAPI.updateSession(
        sessionData.id,
        sessionData,
        user.email
      );
      setSessions(sessions.map((s) => (s.id === updated.id ? updated : s)));
      if (session?.id === updated.id) {
        setSession(updated);
      }
    } else {
      const created = await sessionAPI.createSession(
        {
          ...sessionData,
          name: "Default Session - " + new Date().toLocaleDateString(),
        },
        user.email
      );
      setSessions([created, ...sessions]);
      setSession(created);
    }
    setIsEditorOpen(false);
    setEditingSession(undefined);
  } catch (error) {
    messageApi.error("Error saving session");
  } finally {
    setIsLoading(false);
  }
};
```

For newcomers, note how React hooks (`useState`, `useEffect`, `useCallback`) coordinate UI state with backend responses while keeping the UI responsive.

### Real-time Collaboration Flow
When a user opens a session, the chat experience streams updates through WebSockets. `SessionManager` opens one socket per active session and passes a factory function down to the chat view.

```tsx
// Source: frontend/src/components/views/manager.tsx (lines 273-316)
const setupWebSocket = (sessionId: number, runId: string): WebSocket => {
  if (sessionSockets[sessionId]) {
    sessionSockets[sessionId].socket.close();
  }

  const serverUrl = getServerUrl();
  const baseUrl = getBaseUrl(serverUrl);
  const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${wsProtocol}//${baseUrl}/api/ws/runs/${runId}`;

  const socket = new WebSocket(wsUrl);
  setSessionSockets((prev) => ({
    ...prev,
    [sessionId]: { socket, runId },
  }));

  return socket;
};
```

The chat component binds incoming messages to the UI and surfaces backend requests for additional input.

```tsx
// Source: frontend/src/components/views/chat/chat.tsx (lines 140-189)
const loadSessionRun = async () => {
  if (!session?.id || !user?.email) return null;

  try {
    const response = await sessionAPI.getSessionRuns(session.id, user?.email);
    const latestRun = response.runs[response.runs.length - 1];
    return latestRun;
  } catch (error) {
    messageApi.error("Failed to load chat history");
    return null;
  }
};

React.useEffect(() => {
  const initializeSession = async () => {
    if (session?.id) {
      setActiveSocket(null);
      const latestRun = await loadSessionRun();

      if (latestRun) {
        setCurrentRun(latestRun);
        setNoMessagesYet(latestRun.messages.length === 0);

        if (latestRun.id) {
          setupWebSocket(latestRun.id, false, true);
        }
      } else {
        setError({ status: false, message: "No run found" });
      }
    } else {
      setCurrentRun(null);
    }
  };

  initializeSession();
}, [session?.id, visible]);
```

React newcomers should observe how effect hooks reload chat history when the selected session changes and gracefully handle missing data.

Later in the same file, `setupWebSocket` delegates to the `getSessionSocket` prop supplied by `SessionManager`, which guarantees only one live connection per run while still allowing reconnection when a user refreshes the page.

### Configuration & Feature Panels
Beyond chat, the shell exposes additional panels (Saved Plans, MCP server configuration) powered by Zustand state slices.

```tsx
// Source: frontend/src/components/store.tsx (lines 1-41)
export const useSettingsStore = create<SettingsState>()((set) => ({
  config: defaultConfig,
  updateConfig: (update) =>
    set((state) => ({
      config: { ...state.config, ...update },
    })),
  resetToDefaults: () => set({ config: defaultConfig }),
}));
```

The `useSettingsStore` hook lets any component (for example, `SettingsModal` or `PlanList`) read and write configuration without prop drilling. Zustand’s API mirrors React’s `useState`, which keeps the learning curve shallow for beginners.

### Page-to-Backend Interaction Map

| Frontend entry point | Backend endpoint(s) | Purpose |
| -------------------- | ------------------- | ------- |
| `SessionManager` sidebar actions | `GET/POST/PUT/DELETE /sessions`, `GET /sessions/{id}/runs` | Manage conversational workspaces and load history. |
| `ChatView` WebSocket bridge | `GET /sessions/{id}/runs`, `WS /api/ws/runs/{run_id}` | Stream agent messages, push user replies, and show live status. |
| `PlanList` saved-plan panel | `GET /plans`, `POST /plans/{id}/execute` | Retrieve reusable workflows and launch them into a session. |
| `SettingsModal` configuration form | `GET/POST /settings`, `POST /settings/validate` | Persist agent/team defaults and validate YAML overrides. |
| `signin.tsx` (optional enterprise extension) | `POST /auth/*` (custom) | Integrate with SSO or API key issuance flows. |

This matrix shows how each page or feature module maps to FastAPI handlers. Understanding these relationships helps new contributors trace issues end-to-end: inspect the React component to see which API helper it calls, then follow the REST path into the backend service layer described in the next section.

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

