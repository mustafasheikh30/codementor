import contextlib
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from app.sandbox.config import sandbox_settings


class SandboxError(Exception):
    pass


@dataclass
class SandboxResult:
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    time_ms: int | None = None
    memory_kb: int | None = None
    status: str = "ok"
    message: str | None = None


class SandboxExecutor:
    """Sandboxed code execution with isolation and resource limits.

    SAFETY: Disabled by default. Network disabled by default.
    Never executes code on host unless explicitly enabled AND using isolation.
    This implementation provides a safe, disabled-by-default design with
    proper structure for future integration with Docker/nsjail/firejail.
    """

    def __init__(self) -> None:
        self.enabled = sandbox_settings.sandbox_enabled
        self.network_disabled = sandbox_settings.sandbox_network_disabled
        self.max_output_bytes = sandbox_settings.sandbox_max_output_bytes

    def execute(
        self,
        language: str,
        code: str,
        stdin: str = "",
        time_limit_seconds: float = 2.0,
        memory_limit_mb: int = 256,
    ) -> SandboxResult:
        lang = language.strip().lower()
        if lang not in self._supported_languages():
            raise SandboxError(f"Unsupported language: {language}")

        if not self.enabled:
            return SandboxResult(
                status="disabled",
                message="Sandbox execution is disabled. Enable via SANDBOX_ENABLED=true.",
            )

        # Safety check: never allow network if disabled
        if self.network_disabled:
            pass  # Enforced at execution layer

        # Use isolated temp directory
        workdir = Path(tempfile.mkdtemp(prefix="codementor_exec_"))
        try:
            return self._execute_isolated(
                lang, code, stdin, time_limit_seconds, memory_limit_mb, workdir
            )
        finally:
            with contextlib.suppress(Exception):
                shutil.rmtree(workdir)

    def _supported_languages(self) -> set[str]:
        return {
            "python",
            "python3",
            "py",
            "cpp",
            "c++",
            "c++17",
            "c++20",
            "c",
            "java",
            "rust",
            "go",
            "javascript",
            "node",
            "nodejs",
        }

    def _execute_isolated(
        self,
        lang: str,
        code: str,
        stdin: str,
        time_limit_seconds: float,
        memory_limit_mb: int,
        workdir: Path,
    ) -> SandboxResult:
        # This is a safe design - when enabled, it would use Docker/unshare
        # For safety in this environment, we provide the structure but
        # execution requires explicit external isolation tools
        if sandbox_settings.sandbox_use_docker and shutil.which("docker"):
            return self._execute_docker(
                lang, code, stdin, time_limit_seconds, memory_limit_mb, workdir
            )
        # Fallback: cannot execute safely without isolation tools
        return SandboxResult(
            status="disabled",
            message="No isolation backend available. Requires Docker with proper setup or unshare/nsjail.",
        )

    def _execute_docker(
        self,
        lang: str,
        code: str,
        stdin: str,
        time_limit_seconds: float,
        memory_limit_mb: int,
        workdir: Path,
    ) -> SandboxResult:
        # Write code to file
        if lang in ("python", "python3", "py"):
            code_file = workdir / "main.py"
            image = sandbox_settings.sandbox_docker_image_python
            cmd = ["python", "/app/main.py"]
        elif lang in ("cpp", "c++", "c++17", "c++20"):
            code_file = workdir / "main.cpp"
            image = sandbox_settings.sandbox_docker_image_cpp
            cmd = ["sh", "-c", "g++ -O2 -o /app/main /app/main.cpp && /app/main"]
        elif lang == "java":
            code_file = workdir / "Main.java"
            image = sandbox_settings.sandbox_docker_image_java
            cmd = ["sh", "-c", "cd /app && javac Main.java && java Main"]
        elif lang == "rust":
            code_file = workdir / "main.rs"
            image = sandbox_settings.sandbox_docker_image_rust
            cmd = ["sh", "-c", "rustc -O -o /app/main /app/main.rs && /app/main"]
        elif lang in ("javascript", "node", "nodejs"):
            code_file = workdir / "main.js"
            image = sandbox_settings.sandbox_docker_image_node
            cmd = ["node", "/app/main.js"]
        elif lang == "go":
            code_file = workdir / "main.go"
            image = sandbox_settings.sandbox_docker_image_go
            cmd = ["sh", "-c", "cd /app && go run main.go"]
        elif lang == "c":
            code_file = workdir / "main.c"
            image = sandbox_settings.sandbox_docker_image_cpp
            cmd = ["sh", "-c", "gcc -O2 -o /app/main /app/main.c && /app/main"]
        else:
            raise SandboxError(f"Unsupported language: {lang}")

        code_file.write_text(code)

        # Build docker command with security restrictions
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none" if self.network_disabled else "bridge",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--tmpfs",
            "/app:rw,exec,nosuid,size=256m",
            "-v",
            f"{workdir}:/app:ro",
            "--cpus",
            "1",
            "--memory",
            f"{memory_limit_mb}m",
            "--memory-swap",
            f"{memory_limit_mb}m",
            "--ulimit",
            "nofile=64:64",
            "--ulimit",
            "nproc=64:64",
            "--pids-limit",
            "64",
            "--security-opt",
            "no-new-privileges",
            "--cap-drop",
            "ALL",
        ]
        docker_cmd.extend([image] + cmd)

        start = time.monotonic()
        try:
            proc = subprocess.run(
                docker_cmd,
                input=stdin.encode() if stdin else None,
                capture_output=True,
                timeout=time_limit_seconds + 5,
                check=False,
            )
            elapsed_ms = int((time.monotonic() - start) * 1000)
            stdout = proc.stdout[: self.max_output_bytes].decode(errors="replace")
            stderr = proc.stderr[: self.max_output_bytes].decode(errors="replace")
            status = "ok" if proc.returncode == 0 else "runtime_error"
            return SandboxResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=proc.returncode,
                time_ms=elapsed_ms,
                status=status,
            )
        except subprocess.TimeoutExpired:
            return SandboxResult(status="timeout", message="Execution timed out")
        except (OSError, ValueError) as e:
            return SandboxResult(status="runtime_error", message=str(e))


_executor = SandboxExecutor()


def execute_code(
    language: str,
    code: str,
    stdin: str = "",
    time_limit_seconds: float = 2.0,
    memory_limit_mb: int = 256,
) -> SandboxResult:
    return _executor.execute(language, code, stdin, time_limit_seconds, memory_limit_mb)
