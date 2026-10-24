from fastapi import APIRouter, HTTPException, Request

from app.sandbox import service
from app.sandbox.schemas import ExecutionRequest, ExecutionResult
from app.users.routes import session_user_id

router = APIRouter(prefix="/api", tags=["sandbox"])


def require_user_id(request: Request) -> int:
    user_id = session_user_id(request)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id


@router.post("/sandbox/execute", response_model=ExecutionResult)
def execute(request: Request, payload: ExecutionRequest) -> ExecutionResult:
    require_user_id(request)
    try:
        result = service.execute_code(
            language=payload.language,
            code=payload.code,
            stdin=payload.stdin,
            time_limit_seconds=payload.time_limit_seconds,
            memory_limit_mb=payload.memory_limit_mb,
        )
        return ExecutionResult(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_code,
            time_ms=result.time_ms,
            memory_kb=result.memory_kb,
            status=result.status,
            message=result.message,
        )
    except service.SandboxError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Execution failed") from exc
