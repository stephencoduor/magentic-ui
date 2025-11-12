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
  - [Dependency Injection & Lifespan Hooks](#dependency-injection--lifespan-hooks)
  - [Domain Models & Persistence](#domain-models--persistence)
  - [Real-time Streaming & User Prompts](#real-time-streaming--user-prompts)
  - [Agent Orchestration](#agent-orchestration)
  - [Backend ↔ Frontend Integration](#backend--frontend-integration)
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
The FastAPI stack is intentionally explicit to help newcomers understand where lifecycle hooks, middleware, and routers are declared. The application factory wires up startup, shutdown, and modular routers in one place, so the backend can be embedded in tests or alternative deployments without additional glue code.

```python title="src/magentic_ui/backend/web/app.py"{32-87}
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifecycle manager for the FastAPI application."""
    try:
        config: dict[str, Any] = {}
        config_file = os.environ.get("_CONFIG")
        if config_file:
            logger.info(f"Loading config from file: {config_file}")
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
        else:
            logger.info("No config file provided, using defaults.")

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
        logger.info(
            f"Application startup complete. Navigate to http://{os.environ.get('_HOST', '127.0.0.1')}:{os.environ.get('_PORT', '8081')}"
        )
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

    yield

    try:
        logger.info("Cleaning up application resources...")
        await cleanup_managers()
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

app = FastAPI(lifespan=lifespan, debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://localhost:8081",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api = FastAPI(
    root_path="/api",
    title="Magentic-UI API",
    version=VERSION,
    description="Magentic-UI is an application to interact with web agents.",
    docs_url="/docs" if settings.API_DOCS else None,
)
api.include_router(sessions.router, prefix="/sessions", tags=["sessions"], responses={404: {"description": "Not found"}})
api.include_router(plans.router, prefix="/plans", tags=["plans"], responses={404: {"description": "Not found"}})
```
*Source: `src/magentic_ui/backend/web/app.py`*

Key FastAPI concepts on display:

1. **Application lifespan:** `lifespan` encapsulates startup/shutdown work so that database connections and streaming managers are brought online exactly once per process. New FastAPI users can think of this as the async equivalent of Django’s `ready()` hook.
2. **Sub-application routing:** The project mounts a secondary `FastAPI` instance at `/api`, keeping API schema metadata separate from static asset hosting. Static mounts at `/files` and `/` serve run artifacts and the compiled Gatsby site with the same process.
3. **CORS middleware:** By explicitly listing development origins, the React SPA can call the API during local development without browser errors.

### Dependency Injection & Lifespan Hooks
FastAPI’s dependency system is used heavily to share initialized managers across request handlers. `deps.py` exposes async callables that raise typed HTTP errors whenever initialization is incomplete, which is friendlier for new contributors than allowing attribute errors to bubble up.

```python title="src/magentic_ui/backend/web/deps.py"{21-127}
@contextmanager
def get_db_context():
    if not _db_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database manager not initialized",
        )
    try:
        yield _db_manager
    except Exception as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        ) from e

async def get_db() -> DatabaseManager:
    if not _db_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database manager not initialized",
        )
    return _db_manager

async def init_managers(
    database_uri: str,
    config_dir: Path,
    app_root: Path,
    internal_workspace_root: str,
    external_workspace_root: str,
    inside_docker: bool,
    config: Dict[str, Any],
    run_without_docker: bool,
) -> None:
    _db_manager = DatabaseManager(engine_uri=database_uri, base_dir=app_root)
    _db_manager.initialize_database(auto_upgrade=settings.UPGRADE_DATABASE)
    _websocket_manager = WebSocketManager(
        db_manager=_db_manager,
        internal_workspace_root=Path(internal_workspace_root),
        external_workspace_root=Path(external_workspace_root),
        inside_docker=inside_docker,
        config=config,
        run_without_docker=run_without_docker,
    )
```
*Source: `src/magentic_ui/backend/web/deps.py`*

Because dependencies are declared with `Depends(...)` inside routers, every endpoint automatically receives the same database session manager and connection orchestrator. When you write a new route, you can simply include `db=Depends(get_db)` and focus on business logic instead of connection plumbing.

### Domain Models & Persistence
All persistent records are expressed as [SQLModel](https://sqlmodel.tiangolo.com/) classes, which blend SQLAlchemy’s ORM with Pydantic validation. Reading the models is the quickest way to learn what data the frontend expects.

```python title="src/magentic_ui/backend/datamodel/db.py"{38-144}
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    config: Union[MessageConfig, dict[str, Any]] = Field(
        default_factory=lambda: MessageConfig(source="", content=""),
        sa_column=Column(JSON),
    )
    session_id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("session.id", ondelete="CASCADE")),
    )
    run_id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("run.id", ondelete="CASCADE")),
    )

class Run(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer, ForeignKey("session.id", ondelete="CASCADE"), nullable=False
        ),
    )
    status: RunStatus = Field(default=RunStatus.CREATED)
    task: Union[MessageConfig, dict[str, Any]] = Field(
        default_factory=lambda: MessageConfig(source="", content=""),
        sa_column=Column(JSON),
    )
    team_result: Union[TeamResult, dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    input_request: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
```
*Source: `src/magentic_ui/backend/datamodel/db.py`*

Helpful mental models for beginners:

- **Session** represents the high-level chat workspace owned by a user.
- **Run** captures one execution attempt within a session, including the task prompt, agent outputs, and input requests.
- **Message** stores the streaming transcript. Foreign keys cascade deletes so you never need to manually clean up dependent rows.

Under the hood, `DatabaseManager` centralizes engine creation, schema migrations, and utility helpers such as `reset_db` for local testing. Its constructor configures SQLite pragmas for concurrency, while `initialize_database` optionally triggers automatic migrations when the schema drifts.【F:src/magentic_ui/backend/database/db_manager.py†L16-L147】

### Real-time Streaming & User Prompts
The `/api/ws/runs/{run_id}` route streams task progress, input requests, and completion events to the browser. FastAPI’s WebSocket support pairs nicely with dependency injection so that the same database manager can be reused inside the socket loop.

```python title="src/magentic_ui/backend/web/routes/ws.py"{17-118}
@router.websocket("/runs/{run_id}")
async def run_websocket(
    websocket: WebSocket,
    run_id: int,
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
    db=Depends(get_db),
):
    run_response = db.get(Run, filters={"id": run_id}, return_json=False)
    if not run_response.status or not run_response.data:
        await websocket.close(code=4004, reason="Run not found")
        return

    connected = await ws_manager.connect(websocket, run_id)
    if not connected:
        await websocket.close(code=4002, reason="Failed to establish connection")
        return

    try:
        while True:
            raw_message = await websocket.receive_text()
            message = json.loads(raw_message)
            if message.get("type") == "start":
                task = construct_task(query=message.get("task"), files=message.get("files"))
                team_config = message.get("team_config")
                settings_config = message.get("settings_config")
                if task and team_config:
                    asyncio.create_task(
                        ws_manager.start_stream(run_id, task, team_config, settings_config)
                    )
```
*Source: `src/magentic_ui/backend/web/routes/ws.py`*

`WebSocketManager` handles the heavy lifting: it accepts browser connections, streams `TeamResult` updates from the agent runtime, persists transcript messages, and pauses runs while waiting for human input.

```python title="src/magentic_ui/backend/web/managers/connection.py"{40-120,200-284}
class WebSocketManager:
    def __init__(
        self,
        db_manager: DatabaseManager,
        internal_workspace_root: Path,
        external_workspace_root: Path,
        inside_docker: bool,
        config: Dict[str, Any],
        run_without_docker: bool,
    ):
        self._connections: Dict[int, WebSocket] = {}
        self._input_responses: Dict[int, asyncio.Queue[str]] = {}
        self._team_managers: Dict[int, TeamManager] = {}

    async def start_stream(
        self,
        run_id: int,
        task: str | ChatMessage | Sequence[ChatMessage] | None,
        team_config: Dict[str, Any],
        settings_config: Dict[str, Any],
        user_settings: Settings | None = None,
    ) -> None:
        if run_id not in self._connections or run_id in self._closed_connections:
            raise ValueError(f"No active connection for run {run_id}")

        if run_id not in self._team_managers:
            team_manager = TeamManager(
                internal_workspace_root=self.internal_workspace_root,
                external_workspace_root=self.external_workspace_root,
                inside_docker=self.inside_docker,
                config=self.config,
                run_without_docker=self.run_without_docker,
            )
            self._team_managers[run_id] = team_manager

        async for message in team_manager.run_stream(
            task=task,
            team_config=team_config,
            state=state,
            input_func=input_func,
            cancellation_token=cancellation_token,
            env_vars=env_vars,
            settings_config=settings_config,
            run=run,
        ):
            if (
                cancellation_token.is_cancelled()
                or run_id in self._closed_connections
            ):
                logger.info(
                    f"Stream cancelled or connection closed for run {run_id}"
                )
                break

            if isinstance(message, CheckpointEvent):
                run = await self._get_run(run_id)
                if run:
                    run.state = message.state
                    self.db_manager.upsert(run)
                continue

            formatted_message = self._format_message(message)
            if formatted_message:
                await self._send_message(run_id, formatted_message)
                if isinstance(
                    message,
                    (
                        TextMessage,
                        MultiModalMessage,
                        StopMessage,
                        HandoffMessage,
                        ToolCallRequestEvent,
                        ToolCallExecutionEvent,
                        LLMCallEventMessage,
                    ),
                ):
                    await self._save_message(run_id, message)
                elif isinstance(message, TeamResult):
                    final_result = message.model_dump()
```
*Source: `src/magentic_ui/backend/web/managers/connection.py`*

For newcomers, remember that WebSockets stay open until either side calls `close()`. The manager keeps cancellation tokens, run state, and per-connection queues so that user approvals (`input_response` messages) can be awaited without blocking the entire event loop.

### Agent Orchestration
`TeamManager` bridges the FastAPI surface area with the AutoGen-powered agent teams. It prepares workspace directories, loads the requested team configuration, and streams events back to the WebSocket manager.

```python title="src/magentic_ui/backend/teammanager/teammanager.py"{49-115,174-199}
class TeamManager:
    """Manages team operations including loading configs and running teams"""

    def __init__(
        self,
        internal_workspace_root: Path,
        external_workspace_root: Path,
        run_without_docker: bool,
        inside_docker: bool = True,
        config: dict[str, Any] = {},
    ) -> None:
        self.team: Team | None = None
        self.internal_workspace_root = internal_workspace_root
        self.external_workspace_root = external_workspace_root
        self.inside_docker = inside_docker
        self.run_without_docker = run_without_docker
        self.config = config

    def prepare_run_paths(self, run: Optional[Run] = None) -> RunPaths:
        if run:
            run_suffix = os.path.join(
                "files",
                "user",
                str(run.user_id or "unknown_user"),
                str(run.session_id or "unknown_session"),
                str(run.id or "unknown_run"),
            )
        else:
            run_suffix = os.path.join(
                "files", "user", "unknown_user", "unknown_session", "unknown_run"
            )
        internal_run_dir = internal_workspace_root / Path(run_suffix)
        external_run_dir = external_workspace_root / Path(run_suffix)
        logger.info(f"Creating run dirs: {internal_run_dir} and {external_run_dir}")
        if self.inside_docker:
            internal_run_dir.mkdir(parents=True, exist_ok=True)
        else:
            external_run_dir.mkdir(parents=True, exist_ok=True)

        return RunPaths(
            internal_root_dir=internal_workspace_root,
            external_root_dir=external_workspace_root,
            run_suffix=run_suffix,
            internal_run_dir=internal_run_dir,
            external_run_dir=external_run_dir,
        )

    async def _create_team(
        self,
        team_config: Union[str, Path, Dict[str, Any], ComponentModel],
        state: Optional[Mapping[str, Any] | str] = None,
        input_func: Optional[InputFuncType] = None,
        env_vars: Optional[List[EnvironmentVariable]] = None,
        settings_config: dict[str, Any] = {},
        *,
        paths: RunPaths,
    ) -> tuple[Team, int, int]:
        model_client_from_config_file = ModelClientConfigs(
            orchestrator=self.config.get("orchestrator_client", None),
            web_surfer=self.config.get("web_surfer_client", None),
            coder=self.config.get("coder_client", None),
        )
```
*Source: `src/magentic_ui/backend/teammanager/teammanager.py`*

The orchestration layer is what turns a plain REST API into an autonomous agent playground. It manages AutoGen teams, passes along uploaded files, and returns `TeamResult` payloads that the UI renders as conversation updates.

### Backend ↔ Frontend Integration
Understanding how Gatsby pages call the API makes it easier to extend either side safely. The `SessionManager` component in the frontend relies on a thin REST client (`frontend/src/components/views/api.ts`) plus a dedicated WebSocket for live updates.

| Frontend entry point | Backend dependency | Purpose |
| -------------------- | ------------------ | ------- |
| `SessionAPI.listSessions` fetches `GET /sessions/?user_id=...` to populate the left-hand session list when the workspace loads.【F:frontend/src/components/views/api.ts†L15-L26】【F:src/magentic_ui/backend/web/routes/sessions.py†L13-L27】 | `sessions.router` with `Depends(get_db)` filters records by `user_id`, guaranteeing users only see their own sessions.【F:src/magentic_ui/backend/web/routes/sessions.py†L13-L27】 | Load the initial workspace context. |
| `SessionAPI.createSession` posts to `/sessions/` whenever a user spins up a new conversation from the UI toolbar.【F:frontend/src/components/views/api.ts†L41-L59】 | The backend creates a `Session`, then immediately seeds a `Run` row so the WebSocket has a target ID to stream into.【F:src/magentic_ui/backend/web/routes/sessions.py†L29-L55】 | Ensure every session has at least one executable run. |
| `SessionManager.setupWebSocket` opens `ws://…/api/ws/runs/{runId}` as soon as a run is selected, matching the REST fetches for run history.【F:frontend/src/components/views/manager.tsx†L273-L316】【F:frontend/src/components/views/api.ts†L86-L101】 | The `run_websocket` endpoint validates the run via `get_db` and pipes messages through `WebSocketManager.start_stream`, which streams task state and saves transcripts.【F:src/magentic_ui/backend/web/routes/ws.py†L17-L118】【F:src/magentic_ui/backend/web/managers/connection.py†L115-L284】 | Drive the live transcript, tool events, and approval prompts shown in the conversation pane. |
| When the user edits LLM settings or team composition, the UI reuses `TeamAPI` helpers that call `/teams` routes to fetch and persist templates.【F:frontend/src/components/views/api.ts†L132-L193】 | `teams.router` persists `Team` SQLModel objects so that AutoGen configurations are versioned per user and can be reused across sessions.【F:src/magentic_ui/backend/web/routes/teams.py†L1-L41】 | Keep orchestrator/coder/web-surfer setups in sync between the UI and backend runtime. |

By tracing these flows, you can confidently add new controls to the Gatsby UI and immediately know which FastAPI router to extend or which SQLModel to adjust. Always cross-check line numbers in the repository before copying snippets into documentation or tooling scripts.

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

