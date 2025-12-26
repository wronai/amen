"""
INTENT-ITERATIVE: Web Interface
FastAPI-based web UI for intent management.
"""

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import uuid

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ir.models import IntentIR, ExecutionMode
from parser.dsl_parser import parse_dsl, ParseError, ValidationError
from planner.simulator import plan_intent, DryRunResult
from executor.runner import execute_intent, ExecutionResult


app = FastAPI(
    title="INTENT-ITERATIVE",
    description="DSL-based intent execution system with iterative refinement",
    version="0.1.0"
)

# In-memory storage for intents (in production, use a database)
intents_store: Dict[str, IntentIR] = {}

# Templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


# Pydantic models for API
class DSLInput(BaseModel):
    content: str


class IterationInput(BaseModel):
    changes: Dict[str, Any]
    source: str = "web"


class ExecutionRequest(BaseModel):
    workspace: Optional[str] = None


# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main dashboard."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "intents": list(intents_store.values())
    })


@app.get("/api/intents")
async def list_intents():
    """List all stored intents."""
    return {
        "intents": [
            {
                "id": ir.id,
                "name": ir.intent.name,
                "goal": ir.intent.goal,
                "mode": ir.execution_mode.value,
                "amen_approved": ir.amen_approved,
                "iterations": ir.iteration_count
            }
            for ir in intents_store.values()
        ]
    }


@app.post("/api/intents/parse")
async def parse_intent(data: DSLInput):
    """Parse DSL content and create new intent."""
    try:
        ir = parse_dsl(data.content)
        intents_store[ir.id] = ir
        return {
            "success": True,
            "id": ir.id,
            "intent": ir.to_dict()
        }
    except (ParseError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/intents/{intent_id}")
async def get_intent(intent_id: str):
    """Get intent by ID."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    return intents_store[intent_id].to_dict()


@app.delete("/api/intents/{intent_id}")
async def delete_intent(intent_id: str):
    """Delete intent by ID."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    del intents_store[intent_id]
    return {"success": True, "deleted": intent_id}


@app.post("/api/intents/{intent_id}/plan")
async def plan(intent_id: str):
    """Run dry-run planning for intent."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    result = plan_intent(ir)
    
    return {
        "success": result.success,
        "logs": result.logs,
        "generated_code": result.generated_code,
        "dockerfile": result.dockerfile,
        "warnings": result.warnings,
        "estimated_resources": result.estimated_resources
    }


@app.post("/api/intents/{intent_id}/iterate")
async def iterate(intent_id: str, data: IterationInput):
    """Apply iterative changes to intent."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    ir.add_iteration(data.changes, source=data.source)
    
    # Apply simple changes
    if "action" in data.changes:
        from parser.dsl_parser import DSLParser
        parser = DSLParser()
        action = parser._parse_action(data.changes["action"])
        if action:
            ir.implementation.actions.append(action)
    
    if "framework" in data.changes:
        ir.implementation.framework = data.changes["framework"]
    
    if "language" in data.changes:
        ir.implementation.language = data.changes["language"]
    
    return {
        "success": True,
        "iteration_count": ir.iteration_count,
        "intent": ir.to_dict()
    }


@app.post("/api/intents/{intent_id}/amen")
async def approve_amen(intent_id: str):
    """Approve intent for execution (AMEN boundary)."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    ir.approve_amen()
    
    return {
        "success": True,
        "amen_approved": True,
        "execution_mode": ir.execution_mode.value
    }


@app.post("/api/intents/{intent_id}/execute")
async def execute(intent_id: str, data: ExecutionRequest = None):
    """Execute approved intent."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    
    if not ir.amen_approved:
        raise HTTPException(
            status_code=400, 
            detail="Intent not approved. Call /amen endpoint first."
        )
    
    workspace = data.workspace if data else None
    result = execute_intent(ir, workspace)
    
    return {
        "success": result.success,
        "logs": result.logs,
        "artifacts": result.artifacts,
        "container_id": result.container_id,
        "endpoints": result.endpoints,
        "error": result.error,
        "execution_time": result.execution_time
    }


@app.get("/api/intents/{intent_id}/code")
async def get_generated_code(intent_id: str):
    """Get generated code for intent."""
    if intent_id not in intents_store:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    ir = intents_store[intent_id]
    return {
        "generated_code": ir.generated_code,
        "dockerfile": ir.dockerfile
    }


# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.1.0"}


def create_app() -> FastAPI:
    """Factory function for creating the app."""
    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
