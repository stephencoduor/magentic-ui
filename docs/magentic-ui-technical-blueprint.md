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
  - [Application Shell & Context](#application-shell--context)
  - [Page Routing](#page-routing)
  - [Session Workspace Composition](#session-workspace-composition)
  - [Chat Execution & WebSocket Loop](#chat-execution--websocket-loop)
  - [API Client Bridges to FastAPI](#api-client-bridges-to-fastapi)
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
- **Framework:** Gatsby wraps a React + TypeScript single-page application, letting newcomers reason about the app as a standard React tree while benefiting from Gatsby’s build pipeline defined in `frontend/gatsby-config.ts`.
- **Styling:** TailwindCSS utility classes (configured in `frontend/tailwind.config.js`) combine with Ant Design components for rapid UI assembly.
- **State:** Zustand stores power both UI chrome preferences and agent session state, avoiding Redux boilerplate while remaining fully typed.

### Application Shell & Context
The entire UI tree is wrapped by a provider that seeds default user metadata, dark-mode preference, and helper actions for later components.

```tsx
const Provider = ({ children }: any) => {
  const storedValue = getLocalStorage("darkmode", false);
  const [darkMode, setDarkMode] = useState(
    storedValue === null ? "dark" : storedValue === "dark" ? "dark" : "light"
  );
  const logout = () => {
    console.log("Please implement your own logout logic");
    message.info("Please implement your own logout logic");
  };
  const updateDarkMode = (darkMode: string) => {
    setDarkMode(darkMode);
    setLocalStorage("darkmode", darkMode, false);
  };
  const initUser = {
    name: "Guest User",
    email: getLocalStorage("user_email") || "guestuser@gmail.com",
    username: "guestuser",
  };
  const [userState, setUserState] = useState<IUser | null>(initUser);
  return (
    <appContext.Provider value={{ user: userState, setUser, logout, cookie_name, darkMode, setDarkMode: updateDarkMode }}>
      {children}
    </appContext.Provider>
  );
};
```
*Source: `frontend/src/hooks/provider.tsx` (lines 27-84)*

The application shell supplied by Gatsby renders `MagenticUILayout`, which injects the `SessionManager` view and synchronizes appearance with the context.

```tsx
const MagenticUILayout = ({ title, link, restricted = false }: Props) => {
  const { darkMode, user, setUser } = React.useContext(appContext);
  const { sidebar } = useConfigStore();
  React.useEffect(() => {
    if (!user?.email) {
      const defaultEmail = "default";
      setUser({ ...user, email: defaultEmail, name: defaultEmail });
      window.localStorage.setItem("user_email", defaultEmail);
    }
  }, [user, setUser]);
  return (
    <div className="h-screen flex">
      <ConfigProvider theme={{ algorithm: darkMode === "dark" ? theme.darkAlgorithm : theme.defaultAlgorithm }}>
        <main className="flex-1 p-1 text-primary" style={{ height: "100%" }}>
          <SessionManager />
        </main>
      </ConfigProvider>
    </div>
  );
};
```
*Source: `frontend/src/components/layout.tsx` (lines 23-108)*

### Page Routing
Gatsby’s file-system routing keeps onboarding simple: `pages/index.tsx` mounts the shared layout and forwards build-time metadata into `<head>` tags through Gatsby’s GraphQL query.

```tsx
const IndexPage = ({ data }: any) => {
  return (
    <MagenticUILayout meta={data.site.siteMetadata} title="Home" link={"/"}>
      <main style={{ height: "100%" }} className="h-full" />
    </MagenticUILayout>
  );
};

export const query = graphql`
  query HomePageQuery {
    site {
      siteMetadata {
        description
        title
      }
    }
  }
`;
```
*Source: `frontend/src/pages/index.tsx` (lines 1-26)*

### Session Workspace Composition
`SessionManager` orchestrates sidebar navigation, chat panes, and modal editors. New developers can trace the session lifecycle—list, create, select, and delete—within a single component.

```tsx
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
    console.error("Error fetching sessions:", error);
    messageApi.error("Error loading sessions");
  } finally {
    setIsLoading(false);
  }
}, [user?.email, setSessions, session, setSession]);

return (
  <div className="relative flex flex-col h-full w-full">
    {contextHolder}

    <ContentHeader
      isMobileMenuOpen={isMobileMenuOpen}
      onMobileMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
      isSidebarOpen={isSidebarOpen}
      onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
      onNewSession={() => handleEditSession()}
    />

    <div className="flex flex-1 relative">
      <div
        className={`absolute left-0 top-0 h-full transition-all duration-200 ease-in-out ${
          isSidebarOpen ? "w-77" : "w-0"
        }`}
      >
        <Sidebar
          isOpen={isSidebarOpen}
          sessions={sessions}
          currentSession={session}
          onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
          onSelectSession={handleSelectSession}
          onEditSession={handleEditSession}
          onDeleteSession={handleDeleteSession}
          isLoading={isLoading}
          sessionRunStatuses={sessionRunStatuses}
          activeSubMenuItem={activeSubMenuItem}
          onSubMenuChange={setActiveSubMenuItem}
          onStopSession={(sessionId: number) => {
            if (sessionId === undefined || sessionId === null) return;
            const id = Number(sessionId);
            const ws = sessionSockets[id]?.socket;
            if (ws && ws.readyState === WebSocket.OPEN) {
              ws.send(
                JSON.stringify({
                  type: "stop",
                  reason: "Cancelled by user (sidebar)",
                })
              );
              ws.close();
            }
            setSessionRunStatuses((prev) => ({
              ...prev,
              [id]: "stopped",
            }));
          }}
        />
      </div>

      <div
        className={`flex-1 transition-all -mr-4 duration-200 w-[200px] ${
          isSidebarOpen ? "ml-64" : "ml-0"
        }`}
      >
        {activeSubMenuItem === "mcp_servers" ? (
          <div className="h-full overflow-hidden pl-4">
            <McpServersList />
          </div>
        ) : activeSubMenuItem === "saved_plan" ? (
          <div className="h-full overflow-hidden pl-4">
            <PlanList
              onTabChange={setActiveSubMenuItem}
              onSelectSession={handleSelectSession}
              onCreateSessionFromPlan={handleCreateSessionFromPlan}
            />
          </div>
        ) : session && sessions.length > 0 ? (
          <div className="pl-4">{chatViews}</div>
        ) : (
          <div className="flex items-center justify-center h-full text-secondary">
            <Spin size="large" tip={"Loading..."} />
          </div>
        )}
      </div>

      <SessionEditor
        session={editingSession}
        isOpen={isEditorOpen}
        onSave={handleSaveSession}
        onCancel={() => {
          setIsEditorOpen(false);
          setEditingSession(undefined);
        }}
      />
    </div>
  </div>
);
```
*Source: `frontend/src/components/views/manager.tsx` (lines 59-543)*

### Chat Execution & WebSocket Loop
The chat surface lazily loads the latest run, opens (or reuses) a WebSocket, and streams updates into the UI while tracking agent plan progress. This is the primary bridge between user intent and long-running backend agent activity.

```tsx
const loadSessionRun = async () => {
  if (!session?.id || !user?.email) return null;
  const response = await sessionAPI.getSessionRuns(session.id, user?.email);
  const latestRun = response.runs[response.runs.length - 1];
  return latestRun;
};

React.useEffect(() => {
  if (session?.id) {
    setLocalPlan(null);
    const latestRun = await loadSessionRun();
    if (latestRun) {
      setCurrentRun(latestRun);
      if (latestRun.id) {
        setupWebSocket(latestRun.id, false, true);
      }
    }
  }
}, [session?.id, visible]);
```
*Source: `frontend/src/components/views/chat/chat.tsx` (lines 140-189)*

### API Client Bridges to FastAPI
Front-end API wrappers centralize REST calls so each page consumes typed methods instead of raw `fetch` invocations.

```ts
async listSessions(userId: string): Promise<Session[]> {
  const response = await fetch(
    `${this.getBaseUrl()}/sessions/?user_id=${userId}`,
    { headers: this.getHeaders() }
  );
  const data = await response.json();
  if (!data.status) throw new Error(data.message || "Failed to fetch sessions");
  return data.data;
}

async getSessionRuns(sessionId: number, userId: string): Promise<SessionRuns> {
  const response = await fetch(
    `${this.getBaseUrl()}/sessions/${sessionId}/runs?user_id=${userId}`,
    { headers: this.getHeaders() }
  );
  const data = await response.json();
  if (!data.status) throw new Error(data.message || "Failed to fetch session runs");
  return data.data;
}
```
*Source: `frontend/src/components/views/api.ts` (lines 15-101)*

Each method mirrors a FastAPI route:
- `SessionAPI.listSessions` ⇄ `GET /sessions/` handled by `list_sessions`, returning all user sessions. *Backend source: `src/magentic_ui/backend/web/routes/sessions.py` (lines 13-18).* 
- `SessionAPI.createSession` ⇄ `POST /sessions/`, which persists the session and immediately seeds a `Run` row for streaming. *Backend source: `src/magentic_ui/backend/web/routes/sessions.py` (lines 29-55).* 
- `SessionAPI.updateSession` ⇄ `PUT /sessions/{session_id}`, allowing inline renames from the sidebar editor. *Backend source: `src/magentic_ui/backend/web/routes/sessions.py` (lines 58-77).* 
- `SessionAPI.getSessionRuns` ⇄ `GET /sessions/{session_id}/runs` for chat history and plan metadata. *Backend source: `src/magentic_ui/backend/web/routes/sessions.py` (lines 89-167).* 
- WebSocket commands issued from `ChatView` (`type: "start"`, `"stop"`, `"pause"`, `"resume"`) land in `@router.websocket("/runs/{run_id}")`, where the backend constructs tasks, spins up agent teams, and relays status back to the UI. *Backend source: `src/magentic_ui/backend/web/routes/ws.py` (lines 17-118).* 

By following these pairings, newcomers can read a page/component, locate its API wrapper, and immediately jump into the FastAPI implementation to understand data contracts end-to-end.

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

