"""FastAPI app for regression log analysis."""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.analyzer import analyze_log

app = FastAPI(
    title="AI-Powered Regression Log Analyzer",
    description="Analyze regression logs with transparent rules and optional LLM summaries.",
    version="0.1.0",
)

class LogRequest(BaseModel):
    log_text: str = Field(..., min_length=1, max_length=200_000)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(request: LogRequest):
    result = analyze_log(request.log_text)
    return result

@app.post("/analyze/llm")
def analyze_with_llm(request: LogRequest):
    """Optional OpenAI summary; requires OPENAI_API_KEY and openai package."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Set OPENAI_API_KEY to enable LLM analysis.")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        baseline = analyze_log(request.log_text)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a cautious engineering log assistant. Summarize only evidence in the "
                        "provided log and rule-based analysis. Separate observed facts from hypotheses. "
                        "Never claim a root cause is confirmed without evidence. Keep the answer concise."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Log text:\n{request.log_text}\n\nRule-based analysis:\n{baseline}",
                },
            ],
        )
        return {"rule_based_analysis": baseline, "llm_summary": response.output_text}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {type(exc).__name__}") from exc
