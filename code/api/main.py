from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Prismatic Enrichment API")


class GeminiAnalysis(BaseModel):
    summary: str = ""
    classification: str = ""
    sentiment: str = ""
    confidence_score: float = 1.0
    action_items: str = ""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/categories")
def categories():
    return {
        "categories": [
            "business", "legal", "financial", "hr",
            "medical", "academic", "cybersecurity", "product",
        ]
    }


@app.post("/enrich")
def enrich(analysis: GeminiAnalysis):
    import uuid
    from datetime import datetime, timezone

    department_map = {
        "legal": "Legal", "financial": "Finance", "hr": "Human Resources",
        "medical": "Medical", "academic": "Research", "cybersecurity": "IT Security",
        "product": "Product", "business": "Operations",
    }
    classification = analysis.classification.lower()
    department = department_map.get(classification, "General")

    return {
        "document_id": str(uuid.uuid4()),
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "department": department,
        "routing_tag": f"{department.lower().replace(' ', '-')}-review",
        "confidence_score": round(min(analysis.confidence_score, 1.0), 3),
    }


@app.post("/sensitivity")
def sensitivity(analysis: GeminiAnalysis):
    text = f"{analysis.summary} {analysis.classification}".lower()
    if any(w in text for w in ["confidential", "secret", "classified", "restricted"]):
        level = "confidential"
    elif any(w in text for w in ["internal", "private", "sensitive"]):
        level = "internal"
    else:
        level = "public"
    return {"sensitivity": level}
