from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

app = FastAPI()

class AuditRequest(BaseModel):
    url: str
    target_keyword: str

class AuditSuggestion(BaseModel):
    seo_score: int
    meta_tags: dict
    speed_insights: Optional[dict]
    competitor_comparison: List[dict]
    brand_voice_suggestions: str
    visual_suggestions: str

@app.get("/")
def read_root():
    return {
        "message": "🚀 SEO Audit API is running.",
        "docs": "/docs",
        "status": "ok"
    }

@app.post("/audit", response_model=AuditSuggestion)
def audit_website(request: AuditRequest):
    try:
        page = requests.get(request.url)
        soup = BeautifulSoup(page.content, "html.parser")

        title = soup.title.string if soup.title else ""
        meta_desc = ""
        for tag in soup.find_all("meta"):
            if tag.get("name") == "description":
                meta_desc = tag.get("content")

        meta_tags = {
            "title": title,
            "description": meta_desc,
        }

        serp_url = f"https://serpapi.com/search.json?q={request.target_keyword}&api_key={SERPAPI_KEY}&num=10"
        serp_response = requests.get(serp_url).json()
        competitors = [result['link'] for result in serp_response.get("organic_results", [])[:10]]

        gpt_prompt = f"""
        You are an expert SEO analyst. Analyze this website:

        Title: {title}
        Description: {meta_desc}
        Keyword: {request.target_keyword}
        Competitors: {competitors}

        Suggest:
        - Brand voice improvement
        - Visual suggestions (logo, colors, layout)
        - Content & product presentation changes
        """

        gpt_response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert SEO consultant."},
                {"role": "user", "content": gpt_prompt}
            ]
        )

        suggestions_text = gpt_response['choices'][0]['message']['content']

        return AuditSuggestion(
            seo_score=75,
            meta_tags=meta_tags,
            speed_insights={},
            competitor_comparison=[{"url": url} for url in competitors],
            brand_voice_suggestions=suggestions_text,
            visual_suggestions=suggestions_text
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
