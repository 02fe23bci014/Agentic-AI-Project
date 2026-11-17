import subprocess
import sys
import tempfile
from pathlib import Path

from sandbox.resource_limits import (
    CPU_LIMIT,
    DEFAULT_TIMEOUT_SECONDS,
    MAX_TIMEOUT_SECONDS,
    MEMORY_LIMIT,
    PID_LIMIT,
)
from sandbox.security import validate_language


LANGUAGE_CONFIG = {
    "python": ("programming-lab-python", "main.py", ["python", "/workspace/main.py"]),
    "cpp": (
        "programming-lab-cpp",
        "main.cpp",
        ["sh", "-lc", "g++ -O2 -std=c++17 /workspace/main.cpp -o /tmp/program && /tmp/program"],
    ),
    "java": (
        "programming-lab-java",
        "Main.java",
        [
            "sh",
            "-lc",
            "javac -d /tmp /workspace/Main.java && java -cp /tmp Main",
        ],
    ),
}


def _run_local_fallback(source_path: Path, language: str, stdin: str, timeout: int) -> dict[str, object]:
    """Fallback runner when Docker engine is unavailable."""
    try:
        if language == "python":
            proc = subprocess.run(
                [sys.executable, str(source_path)],
                input=stdin,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
            return {
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode,
                "timed_out": False,
            }
        elif language == "cpp":
            exe_path = source_path.with_suffix(".exe" if sys.platform == "win32" else "")
            compile_proc = subprocess.run(
                ["g++", "-O2", str(source_path), "-o", str(exe_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            if compile_proc.returncode != 0:
                return {
                    "stdout": "",
                    "stderr": compile_proc.stderr,
                    "returncode": compile_proc.returncode,
                    "timed_out": False,
                }
            run_proc = subprocess.run(
                [str(exe_path)],
                input=stdin,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
            return {
                "stdout": run_proc.stdout,
                "stderr": run_proc.stderr,
                "returncode": run_proc.returncode,
                "timed_out": False,
            }
        elif language == "java":
            compile_proc = subprocess.run(
                ["javac", str(source_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            if compile_proc.returncode != 0:
                return {
                    "stdout": "",
                    "stderr": compile_proc.stderr,
                    "returncode": compile_proc.returncode,
                    "timed_out": False,
                }
            run_proc = subprocess.run(
                ["java", "-cp", str(source_path.parent), "Main"],
                input=stdin,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
            return {
                "stdout": run_proc.stdout,
                "stderr": run_proc.stderr,
                "returncode": run_proc.returncode,
                "timed_out": False,
            }
        return {
            "stdout": "",
            "stderr": f"Unsupported language: {language}",
            "returncode": 1,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as error:
        return {
            "stdout": error.stdout or "",
            "stderr": error.stderr or "Execution timed out",
            "returncode": None,
            "timed_out": True,
        }
    except Exception as exc:
        return {
            "stdout": "",
            "stderr": f"Local execution error: {exc}",
            "returncode": 1,
            "timed_out": False,
        }


def run_code(source_code: str, language: str, stdin: str = "", timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> dict[str, object]:
    normalized = validate_language(language)
    if not source_code.strip():
        raise ValueError("Source code cannot be empty")
    timeout = max(1, min(timeout_seconds, MAX_TIMEOUT_SECONDS))
    image, filename, command = LANGUAGE_CONFIG[normalized]
    with tempfile.TemporaryDirectory(prefix="lab-run-") as temp_dir:
        source_path = Path(temp_dir) / filename
        source_path.write_text(source_code, encoding="utf-8")
        docker_command = [
            "docker", "run", "--rm", "-i",
            "--network", "none",
            "--memory", MEMORY_LIMIT,
            "--cpus", CPU_LIMIT,
            "--pids-limit", str(PID_LIMIT),
            "--read-only",
            "--tmpfs", "/tmp:rw,exec,nosuid,size=32m",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--mount", f"type=bind,source={temp_dir},target=/workspace,readonly",
            image,
            *command,
        ]
        try:
            completed = subprocess.run(
                docker_command,
                input=stdin,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
            # If docker failed because daemon/npipe is unreachable, fallback to local execution
            docker_errors = ["docker API", "daemon is not running", "Cannot connect to the Docker daemon", "pipe/docker"]
            if completed.returncode != 0 and any(err in completed.stderr for err in docker_errors):
                return _run_local_fallback(source_path, normalized, stdin, timeout)

            return {
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "returncode": completed.returncode,
                "timed_out": False,
            }
        except (subprocess.TimeoutExpired) as error:
            return {
                "stdout": error.stdout or "",
                "stderr": error.stderr or "Execution timed out",
                "returncode": None,
                "timed_out": True,
            }
        except (FileNotFoundError, OSError):
            return _run_local_fallback(source_path, normalized, stdin, timeout)
