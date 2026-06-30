from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from agents.code_intel import CodeIntelAgent
from agents.debug import DebugAgent
from agents.knowledge import KnowledgeAgent
from agents.devops import DevOpsAgent
from agents.router import MultiModelRouter
from agents.simulator import simulate_autonomous_loop

app = FastAPI(title="Engineering Intelligence Network (EIN) API", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    query: str
    mode: str = "chat"  # "chat" or "builder"
    model: str = "gemini-2.5-flash"
    project_dir: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    response: str
    agent_used: str
    metrics: Dict[str, Any]
    data: Optional[Dict[str, Any]] = None

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ein-backend"}

@app.post("/api/v1/agent/stream")
async def stream_agent(request: AgentRequest):
    """
    Streaming endpoint that returns Server-Sent Events (SSE)
    showing the autonomous multi-agent reasoning loop.
    """
    return StreamingResponse(
        simulate_autonomous_loop(
            query=request.query, 
            mode=request.mode,
            model_name=request.model, 
            project_dir=request.project_dir
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/v1/agent/query", response_model=AgentResponse)
async def query_agent(request: AgentRequest):
    q = request.query.lower()
    router = MultiModelRouter()
    
    # Simple keyword-based routing for demonstration
    if "code" in q or "refactor" in q or "architecture" in q:
        agent = CodeIntelAgent()
        model = router.route("coding", len(q))
        res = agent.analyze_code(q)
        return AgentResponse(
            response=res["explanation"] + " " + res["refactor_plan"],
            agent_used=agent.name,
            metrics={"model": model},
            data=res
        )
    elif "log" in q or "error" in q or "debug" in q:
        agent = DebugAgent()
        model = router.route("debugging", len(q))
        res = agent.analyze_logs([q])
        return AgentResponse(
            response=f"Found root cause: {res['root_cause']}",
            agent_used=agent.name,
            metrics={"model": model, "confidence": res["confidence_score"]},
            data=res
        )
    elif "deploy" in q or "pipeline" in q or "ci/cd" in q:
        agent = DevOpsAgent()
        model = router.route("planning", len(q))
        res = agent.check_pipeline_status("current_repo")
        return AgentResponse(
            response=f"Pipeline {res['status']} at step {res['failing_step']}.",
            agent_used=agent.name,
            metrics={"model": model},
            data=res
        )
    else:
        agent = KnowledgeAgent()
        model = router.route("search", len(q))
        res = agent.semantic_search(q)
        return AgentResponse(
            response=agent.generate_synthesis(q, res),
            agent_used=agent.name,
            metrics={"model": model},
            data={"results": res}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
