import os
import shutil
import uuid
import logging
from typing import Dict
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.pipeline import MatchAnalysisPipeline

# Setup Logging
from src.utils import setup_logger
logger = setup_logger("badminton_cv.web")

app = FastAPI(title="Badminton CV API", version="1.0")

# CORS (Allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, spec domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# State Store (In-memory for MVP, DB for Prod)
class TaskState:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

tasks: Dict[str, Dict] = {}

# Directories
UPLOAD_DIR = "data/uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

class AnalysisResponse(BaseModel):
    task_id: str
    status: str

def run_analysis_task(task_id: str, video_path: str):
    """Background task wrapper."""
    try:
        tasks[task_id]["status"] = TaskState.PROCESSING
        logger.info(f"Task {task_id}: Starting analysis for {video_path}")
        
        # Initialize pipeline (re-init per task to clear state, or reuse if stateless enough)
        # Our pipeline has state (metrics, events), so better new instance.
        pipeline = MatchAnalysisPipeline()
        
        # We need to capture the report output location.
        # The pipeline currently writes to 'outputs/coaching_report.md' hardcoded-ish.
        # We should modify pipeline to accept output path or move file after.
        # For MVP, we let it run and assume standard output location.
        pipeline.run(video_path)
        
        # Basic file management: Return the default report path
        # ideally we rename it to match task_id
        default_report = os.path.join(OUTPUT_DIR, "coaching_report.md")
        task_report = os.path.join(OUTPUT_DIR, f"{task_id}_report.md")
        if os.path.exists(default_report):
            shutil.copy(default_report, task_report)

        tasks[task_id]["status"] = TaskState.COMPLETED
        tasks[task_id]["result"] = {
            "report_path": task_report,
            "video_path": video_path # In real app, annotated video
        }
        logger.info(f"Task {task_id}: Completed successfully.")
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}", exc_info=True)
        tasks[task_id]["status"] = TaskState.FAILED
        tasks[task_id]["error"] = str(e)

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload video and start analysis."""
    task_id = str(uuid.uuid4())
    
    file_path = os.path.join(UPLOAD_DIR, f"{task_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    tasks[task_id] = {
        "status": TaskState.PENDING,
        "filename": file.filename
    }
    
    background_tasks.add_task(run_analysis_task, task_id, file_path)
    
    return {"task_id": task_id, "status": TaskState.PENDING}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if tasks[task_id]["status"] != TaskState.COMPLETED:
        return JSONResponse(status_code=202, content=tasks[task_id])
        
    # Read Markdown Report
    report_path = tasks[task_id]["result"]["report_path"]
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            content = f.read()
        return {"report_markdown": content}
    else:
        return {"error": "Report file not found"}

@app.get("/video/{task_id}")
async def get_video_stream(task_id: str):
    # Retrieve original or annotated video
    # For now, return original
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Hack: just find the file in uploads
    # In prod, store path in task dict
    filename = tasks[task_id].get("filename")
    path = os.path.join(UPLOAD_DIR, f"{task_id}_{filename}")
    
    if not os.path.exists(path):
         raise HTTPException(status_code=404, detail="Video not found")
         
    return FileResponse(path, media_type="video/mp4")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
