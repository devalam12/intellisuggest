from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pydantic import BaseModel
from typing import List, Optional
import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()  # ADD THIS LINE - loads your .env file

app = FastAPI(title="IntelliSuggest API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

DOMAINS = {
    "movies": {
        "catalog": [
            "Interstellar", "The Matrix", "Parasite", "Inception", "The Godfather",
            "Spirited Away", "Arrival", "Her", "Blade Runner 2049", "Everything Everywhere All at Once",
            "The Shawshank Redemption", "Eternal Sunshine of the Spotless Mind", "Whiplash",
            "Dune", "Oppenheimer", "The Grand Budapest Hotel", "Portrait of a Lady on Fire",
            "Mulholland Drive", "Children of Men", "Moon", "Ex Machina", "Annihilation",
            "The Lighthouse", "Hereditary", "Midsommar", "Get Out", "Knives Out",
            "Mad Max: Fury Road", "1917", "Dunkirk", "Tenet", "The Prestige"
        ],
        "schema_fields": "genres, themes, tone (dark/light/neutral), pacing (slow-burn/fast), setting preferences, deal_breakers, loved_examples, hated_examples"
    },
    "books": {
        "catalog": [
            "Dune", "Project Hail Mary", "The Name of the Wind", "Sapiens", "Atomic Habits",
            "The Road", "Never Let Me Go", "Educated", "The Remains of the Day", "Normal People",
            "Blood Meridian", "East of Eden", "The Brothers Karamazov", "Crime and Punishment",
            "Thinking Fast and Slow", "The Man from the Future", "Gödel Escher Bach",
            "A Little Life", "The Sympathizer", "Lincoln in the Bardo", "Piranesi",
            "The Midnight Library", "Fourth Wing", "Tomorrow and Tomorrow and Tomorrow",
            "The Power of the Dog", "No Longer Human", "Kafka on the Shore"
        ],
        "schema_fields": "genres, themes, writing_style (literary/commercial/dense/breezy), length_preference, setting, character_vs_plot_driven, deal_breakers, loved_examples"
    },
    "careers": {
        "catalog": [
            "Software Engineer", "Product Manager", "Data Scientist", "UX Designer",
            "Machine Learning Engineer", "DevOps Engineer", "Solutions Architect",
            "Technical Writer", "Cybersecurity Analyst", "Quantitative Analyst",
            "Research Scientist", "AI Ethics Researcher", "Platform Engineer",
            "Developer Advocate", "Engineering Manager", "Chief Technology Officer",
            "Startup Founder", "Venture Capitalist", "Technical Recruiter",
            "Blockchain Developer", "AR/VR Developer", "Robotics Engineer"
        ],
        "schema_fields": "skills_enjoyed, work_style (collaborative/solo/mixed), environment (remote/office/hybrid), values (impact/income/growth/stability), strengths, disliked_tasks, experience_level"
    },
    "restaurants": {
        "catalog": [
            "Nobu", "Noma", "Eleven Madison Park", "Le Bernardin", "Alinea",
            "The French Laundry", "Osteria Francescana", "Gaggan", "Central", "Geranium",
            "Joe's Pizza", "In-N-Out Burger", "Shake Shack", "Chipotle", "Sweetgreen",
            "Momofuku", "Carbone", "Balthazar", "Per Se", "Daniel",
            "Chez Panisse", "State Bird Provisions", "Flour + Water", "Zuni Café"
        ],
        "schema_fields": "cuisine_types, price_range, atmosphere (casual/formal/vibrant/quiet), dietary_restrictions, occasion (date/family/business/solo), flavor_profiles, deal_breakers"
    }
}


class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    domain: str
    session_id: Optional[str] = None

class PreferenceRequest(BaseModel):
    conversation: str
    domain: str

class RecommendRequest(BaseModel):
    preferences: dict
    domain: str
    feedback: Optional[str] = None


SYSTEM_PROMPT = """You are IntelliSuggest, an expert AI recommendation assistant. Your job is to have a warm, curious conversation to understand what someone genuinely loves and hates — going beyond surface preferences to find deeper patterns.

Ask 2-3 targeted follow-up questions per response. Be conversational, not clinical. Reference specific things they mentioned. Build rapport.

When you have enough information (after 3-4 exchanges), output EXACTLY this JSON block and nothing else before or after it:

<preferences_ready>
{json_schema}
</preferences_ready>

Then add a warm closing message like "Perfect, I have a great sense of your taste — let me find your matches!"

IMPORTANT: Only output the <preferences_ready> block when you truly have enough information to make great recommendations."""


def get_system_prompt(domain: str) -> str:
    schema_fields = DOMAINS.get(domain, {}).get("schema_fields", "genres, themes, preferences, deal_breakers")
    return SYSTEM_PROMPT.replace("{json_schema}", f'{{"domain": "{domain}", {schema_fields}: "...extracted values...","confidence": 0.0-1.0}}')


# @app.get("/")
# def root():
#     return {"status": "IntelliSuggest API running", "version": "1.0.0"}

@app.get("/health")
def root():
    return {"status": "IntelliSuggest API running", "version": "1.0.0"}


@app.get("/domains")
def get_domains():
    return {"domains": list(DOMAINS.keys())}


@app.post("/chat")
async def chat(request: ChatRequest):
    if request.domain not in DOMAINS:
        raise HTTPException(status_code=400, detail=f"Domain must be one of: {list(DOMAINS.keys())}")

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=get_system_prompt(request.domain),
        messages=messages,
    )
    return {"text": response.content[0].text}


@app.post("/recommend")
async def recommend(request: RecommendRequest):
    """Generate ranked recommendations with reasoning from extracted preferences."""
    if request.domain not in DOMAINS:
        raise HTTPException(status_code=400, detail=f"Domain not found")

    catalog = DOMAINS[request.domain]["catalog"]
    prefs_str = json.dumps(request.preferences, indent=2)
    feedback_str = f"\n\nUser feedback on previous recommendations: {request.feedback}" if request.feedback else ""

    prompt = f"""You are a world-class {request.domain} recommendation engine.

User preference profile:
{prefs_str}
{feedback_str}

Available catalog to recommend from:
{json.dumps(catalog)}

Return ONLY valid JSON in this exact format, no other text:
{{
  "recommendations": [
    {{
      "title": "exact title from catalog",
      "match_score": 0.0-1.0,
      "why_youll_love_it": "2 sentences personalized to their specific preferences",
      "key_matches": ["specific preference it matches", "another match"],
      "potential_caveat": "one honest potential downside if any, or null",
      "vibe_tags": ["tag1", "tag2", "tag3"]
    }}
  ],
  "recommendation_rationale": "1 sentence explaining your overall curation strategy"
}}

Pick the best 5 matches. Be specific and personal in your reasoning. Reference their actual stated preferences."""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        data = json.loads(raw)
        return data
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse recommendation response")


@app.post("/extract-preferences")
async def extract_preferences(request: PreferenceRequest):
    """Extract structured preferences from a conversation."""
    schema_fields = DOMAINS.get(request.domain, {}).get("schema_fields", "preferences")

    prompt = f"""Extract a structured preference profile from this conversation about {request.domain}.

Conversation:
{request.conversation}

Return ONLY valid JSON with these fields: domain, {schema_fields}, confidence (0.0-1.0).
No other text, no markdown, just JSON."""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse preferences")

# Serve Angular frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")