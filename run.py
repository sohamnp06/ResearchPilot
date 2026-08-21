#!/usr/bin/env python3
"""
ResearchPilot — Single-Command Startup Script

Usage:
    python run.py

This script:
1. Validates the environment
2. Detects / starts Ollama
3. Starts the backend (FastAPI/uvicorn)
4. Starts the frontend (Vite dev server)
5. Runs health checks on all services
6. Keeps everything running until Ctrl+C
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
import time
import threading
import webbrowser
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8080
FRONTEND_PORT = 5173
OLLAMA_PORT   = 11434

BACKEND_URL  = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"
OLLAMA_URL   = f"http://localhost:{OLLAMA_PORT}"

IS_WINDOWS = platform.system() == "Windows"

# ──────────────────────────────────────────────────────────────────────────────
# COLOURS
# ──────────────────────────────────────────────────────────────────────────────

def _supports_colour() -> bool:
    return sys.stdout.isatty() and IS_WINDOWS is False or os.environ.get("TERM", "") != ""

GREEN  = "\033[92m" if _supports_colour() else ""
RED    = "\033[91m" if _supports_colour() else ""
YELLOW = "\033[93m" if _supports_colour() else ""
CYAN   = "\033[96m" if _supports_colour() else ""
BOLD   = "\033[1m"  if _supports_colour() else ""
RESET  = "\033[0m"  if _supports_colour() else ""

def ok(label: str, detail: str = "") -> None:
    suffix = f"  {detail}" if detail else ""
    print(f"  {GREEN}[OK]{RESET}    {label}{suffix}")

def fail(label: str, reason: str = "") -> None:
    suffix = f"\n          Reason: {reason}" if reason else ""
    print(f"  {RED}[FAILED]{RESET} {label}{suffix}")

def warn(label: str, detail: str = "") -> None:
    suffix = f"  {detail}" if detail else ""
    print(f"  {YELLOW}[WARN]{RESET}   {label}{suffix}")

def info(msg: str) -> None:
    print(f"  {CYAN}>{RESET} {msg}")

def header(msg: str) -> None:
    print(f"\n{BOLD}{msg}{RESET}")

# ──────────────────────────────────────────────────────────────────────────────
# HTTP HELPERS (no external deps — stdlib only)
# ──────────────────────────────────────────────────────────────────────────────

def _http_get(url: str, timeout: float = 5.0) -> tuple[int, str]:
    """Simple HTTP GET using urllib (no requests required)."""
    import urllib.request
    import urllib.error
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, str(exc)
    except Exception as exc:
        return 0, str(exc)

def wait_for_http(url: str, label: str, timeout: int = 120, interval: float = 2.0) -> bool:
    """Poll until URL returns HTTP 2xx or timeout expires."""
    deadline = time.time() + timeout
    dots = 0
    while time.time() < deadline:
        code, _ = _http_get(url)
        if 200 <= code < 300 or code == 307:
            return True
        dots += 1
        sys.stdout.write(f"\r  {CYAN}>{RESET} Waiting for {label}{'.' * (dots % 4):<4}")
        sys.stdout.flush()
        time.sleep(interval)
    sys.stdout.write("\r" + " " * 60 + "\r")
    return False

# ──────────────────────────────────────────────────────────────────────────────
# ENVIRONMENT CHECK
# ──────────────────────────────────────────────────────────────────────────────

def check_env() -> bool:
    """Verify .env exists and has required keys."""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        fail(".env file", "Not found — copy .env.example to .env and fill in values.")
        return False

    env_text = env_file.read_text(encoding="utf-8")
    required = ["secret_key", "SEMANTIC_SCHOLAR_API_KEY"]
    missing  = [k for k in required if k not in env_text or f"{k}=" not in env_text]

    if missing:
        warn(".env", f"Missing keys: {', '.join(missing)}")
    else:
        ok(".env", "All required keys present")

    return True

def load_env() -> None:
    """Load .env into os.environ."""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value

# ──────────────────────────────────────────────────────────────────────────────
# PYTHON / VENV CHECK
# ──────────────────────────────────────────────────────────────────────────────

def check_python() -> bool:
    version = sys.version_info
    if version < (3, 10):
        fail("Python", f"Requires 3.10+, found {version.major}.{version.minor}")
        return False
    ok("Python", f"{version.major}.{version.minor}.{version.micro}")
    return True

def get_python_executable() -> str:
    """Return the Python interpreter to use (prefer venv)."""
    # Windows venv
    candidates = [
        PROJECT_ROOT / "venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / "venv" / "bin" / "python",
        PROJECT_ROOT / ".venv" / "bin" / "python",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return sys.executable

def get_pip_executable() -> str:
    venv_pip_win  = PROJECT_ROOT / "venv" / "Scripts" / "pip.exe"
    venv_pip_unix = PROJECT_ROOT / "venv" / "bin" / "pip"

    if venv_pip_win.exists():
        return str(venv_pip_win)
    if venv_pip_unix.exists():
        return str(venv_pip_unix)

    return "pip"

# ──────────────────────────────────────────────────────────────────────────────
# OLLAMA CHECK / START
# ──────────────────────────────────────────────────────────────────────────────

_ollama_proc: subprocess.Popen | None = None

def check_or_start_ollama() -> bool:
    global _ollama_proc

    provider = os.environ.get("LLM_PROVIDER", "openrouter").lower()
    if provider == "openrouter":
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if api_key:
            ok("OpenRouter API", "Key configured")
            return True
        else:
            warn("OpenRouter API", "OPENROUTER_API_KEY missing in .env")
            return False

    # Is Ollama already running?
    code, _ = _http_get(f"{OLLAMA_URL}/api/tags", timeout=3)
    if 200 <= code < 300:
        ok("Ollama", "Already running")
        return True

    # Try to start Ollama
    info("Ollama not detected — attempting to start...")

    ollama_cmd = "ollama.exe" if IS_WINDOWS else "ollama"

    try:
        _ollama_proc = subprocess.Popen(
            [ollama_cmd, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0,
        )
    except FileNotFoundError:
        fail(
            "Ollama",
            "Not installed. Install from https://ollama.com then run: ollama pull llama3.2",
        )
        return False
    except Exception as exc:
        fail("Ollama", str(exc))
        return False

    # Wait for Ollama to become healthy
    if wait_for_http(f"{OLLAMA_URL}/api/tags", "Ollama", timeout=30):
        ok("Ollama", "Started successfully")
        return True

    fail("Ollama", "Started but did not respond in time")
    return False

# ──────────────────────────────────────────────────────────────────────────────
# BACKEND
# ──────────────────────────────────────────────────────────────────────────────

_backend_proc: subprocess.Popen | None = None

def start_backend() -> bool:
    global _backend_proc

    python = get_python_executable()
    backend_dir = PROJECT_ROOT / "backend"

    # Add project root to PYTHONPATH so backend can import RAG package
    env = os.environ.copy()
    existing_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(PROJECT_ROOT) + (os.pathsep + existing_path if existing_path else "")

    cmd = [
        python, "-m", "uvicorn",
        "app.main:app",
        "--host", BACKEND_HOST,
        "--port", str(BACKEND_PORT),
        "--log-level", "warning",
    ]

    info(f"Starting backend on {BACKEND_URL} ...")

    try:
        _backend_proc = subprocess.Popen(
            cmd,
            cwd=str(backend_dir),
            env=env,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    except Exception as exc:
        fail("Backend", str(exc))
        return False

    # Wait for backend health
    if wait_for_http(f"{BACKEND_URL}/health", "Backend", timeout=90):
        ok("Backend", BACKEND_URL)
        return True

    fail("Backend", "Did not respond at /health in time. Check logs above.")
    return False

# ──────────────────────────────────────────────────────────────────────────────
# FRONTEND
# ──────────────────────────────────────────────────────────────────────────────

_frontend_proc: subprocess.Popen | None = None

def start_frontend() -> bool:
    global _frontend_proc

    frontend_dir = PROJECT_ROOT / "frontend"

    if not (frontend_dir / "node_modules").exists():
        info("node_modules not found — running npm install...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=str(frontend_dir),
                check=True,
                shell=IS_WINDOWS,
            )
        except subprocess.CalledProcessError as exc:
            fail("Frontend (npm install)", str(exc))
            return False

    info(f"Starting frontend on {FRONTEND_URL} ...")

    try:
        _frontend_proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir),
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=IS_WINDOWS,
            creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0,
        )
    except Exception as exc:
        fail("Frontend", str(exc))
        return False

    if wait_for_http(FRONTEND_URL, "Frontend", timeout=60):
        ok("Frontend", FRONTEND_URL)
        return True

    fail("Frontend", f"Did not respond at {FRONTEND_URL} in time.")
    return False

# ──────────────────────────────────────────────────────────────────────────────
# HEALTH DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────

def run_health_checks() -> dict:
    results = {}

    # Database + RAG status from backend /health
    code, body = _http_get(f"{BACKEND_URL}/health")
    if 200 <= code < 300:
        import json
        try:
            data = json.loads(body)
            results["database"] = True
            results["rag"] = data.get("rag_initialized", False)
            results["indexed"] = data.get("indexed_papers", 0)
        except Exception:
            results["database"] = True
            results["rag"] = False
            results["indexed"] = 0
    else:
        results["database"] = False
        results["rag"] = False

    # Semantic Scholar
    ss_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    headers_str = f"x-api-key: {ss_key}" if ss_key else ""
    code, _ = _http_get("https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1")
    results["semantic_scholar"] = 200 <= code < 500  # 400 is still "available"

    # arXiv
    code, _ = _http_get("https://export.arxiv.org/api/query?search_query=all:test&max_results=1", timeout=10)
    results["arxiv"] = 200 <= code < 300

    # LLM check
    provider = os.environ.get("LLM_PROVIDER", "openrouter").lower()
    if provider == "openrouter":
        results["llm"] = bool(os.environ.get("OPENROUTER_API_KEY", ""))
    else:
        code, _ = _http_get(f"{OLLAMA_URL}/api/tags", timeout=5)
        results["llm"] = 200 <= code < 300

    return results

def print_health_dashboard(checks: dict) -> None:
    header("ResearchPilot — Service Status")

    provider = os.environ.get("LLM_PROVIDER", "openrouter").upper()

    _chk("Backend",          True)
    _chk("Frontend",         True)
    _chk("Database",         checks.get("database", False))
    _chk("Embedding Model",  checks.get("rag", False),
         "(loading in background...)" if not checks.get("rag") else "LOADED")
    _chk("FAISS",            checks.get("rag", False))
    _chk(f"{provider} / LLM", checks.get("llm", False))
    _chk("Semantic Scholar", checks.get("semantic_scholar", False))
    _chk("arXiv",            checks.get("arxiv", False))

    if checks.get("indexed", 0):
        info(f"{checks['indexed']} paper(s) already indexed in FAISS")

def _chk(label: str, passed: bool, detail: str = "") -> None:
    if passed:
        ok(label, detail)
    else:
        fail(label)

# ──────────────────────────────────────────────────────────────────────────────
# CLEANUP
# ──────────────────────────────────────────────────────────────────────────────

def cleanup() -> None:
    for proc, name in [
        (_backend_proc,  "Backend"),
        (_frontend_proc, "Frontend"),
        (_ollama_proc,   "Ollama"),
    ]:
        if proc and proc.poll() is None:
            info(f"Stopping {name}...")
            if IS_WINDOWS:
                # `npm run dev` starts child processes. Terminating only the
                # command shell leaves Vite attached to the terminal, which
                # prevents PowerShell from returning to its prompt.
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            else:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()

# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main() -> int:
    print()
    print(f"{BOLD}{'═' * 52}{RESET}")
    print(f"{BOLD}  ResearchPilot — Starting Up{RESET}")
    print(f"{BOLD}{'═' * 52}{RESET}")
    print()

    load_env()

    header("Checking Prerequisites")
    if not check_python():
        return 1
    if not check_env():
        return 1

    header("Starting Services")

    # 1. LLM Provider setup
    llm_ok = check_or_start_ollama()
    if not llm_ok:
        warn("LLM Provider", "Check .env configuration for OPENROUTER_API_KEY.")

    # 2. Backend (fatal if fails)
    if not start_backend():
        print(f"\n  {RED}Backend failed to start. Aborting.{RESET}\n")
        cleanup()
        return 1

    # 3. Frontend (fatal if fails)
    if not start_frontend():
        print(f"\n  {RED}Frontend failed to start. Aborting.{RESET}\n")
        cleanup()
        return 1

    # 4. Health checks
    header("Running Health Checks")
    time.sleep(3)  # Give backend time to finish RAG init
    checks = run_health_checks()
    print_health_dashboard(checks)

    # 5. Ready banner
    print()
    print(f"{BOLD}{'═' * 52}{RESET}")
    print(f"{BOLD}{GREEN}  ResearchPilot is ready!{RESET}")
    print(f"{BOLD}{'═' * 52}{RESET}")
    print()
    print(f"  {CYAN}Frontend:{RESET}  {FRONTEND_URL}")
    print(f"  {CYAN}Backend: {RESET}  {BACKEND_URL}")
    print(f"  {CYAN}API Docs:{RESET}  {BACKEND_URL}/docs")
    print()
    print(f"  {YELLOW}Press Ctrl+C to stop all services.{RESET}")
    print()

    # Launch home page in browser
    try:
        webbrowser.open(FRONTEND_URL)
    except Exception:
        pass

    # 6. Keep running — monitor subprocesses
    try:
        while True:
            time.sleep(5)

            # Check if critical processes died
            if _backend_proc and _backend_proc.poll() is not None:
                print(f"\n  {RED}[ERROR]{RESET} Backend process exited unexpectedly.")
                break

            if _frontend_proc and _frontend_proc.poll() is not None:
                print(f"\n  {RED}[ERROR]{RESET} Frontend process exited unexpectedly.")
                break

    except KeyboardInterrupt:
        print(f"\n\n  {YELLOW}Ctrl+C received — shutting down...{RESET}\n")

    cleanup()
    print(f"  {GREEN}Shutdown complete.{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
