"""
Integration tests for IntelliSuggest API.
Run: pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "IntelliSuggest API running"


def test_get_domains():
    response = client.get("/domains")
    assert response.status_code == 200
    data = response.json()
    assert "domains" in data
    assert "movies" in data["domains"]
    assert "books" in data["domains"]


def test_recommend_invalid_domain():
    response = client.post("/recommend", json={
        "preferences": {"domain": "invalid"},
        "domain": "invalid"
    })
    assert response.status_code == 400


@patch("main.client")
def test_recommend_returns_structured_response(mock_client):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "recommendations": [
            {
                "title": "Interstellar",
                "match_score": 0.95,
                "why_youll_love_it": "A mind-bending sci-fi epic.",
                "key_matches": ["sci-fi", "emotional depth"],
                "potential_caveat": None,
                "vibe_tags": ["epic", "emotional", "sci-fi"]
            }
        ],
        "recommendation_rationale": "Curated for your love of cerebral sci-fi."
    }))]
    mock_client.messages.create.return_value = mock_response

    response = client.post("/recommend", json={
        "preferences": {
            "domain": "movies",
            "genres": ["sci-fi"],
            "themes": ["space", "time"],
            "confidence": 0.9
        },
        "domain": "movies"
    })

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    rec = data["recommendations"][0]
    assert "title" in rec
    assert "match_score" in rec
    assert "why_youll_love_it" in rec


@patch("main.client")
def test_extract_preferences(mock_client):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "domain": "movies",
        "genres": ["sci-fi", "thriller"],
        "themes": ["time travel", "mind-bending"],
        "tone": "dark",
        "confidence": 0.88
    }))]
    mock_client.messages.create.return_value = mock_response

    response = client.post("/extract-preferences", json={
        "conversation": "I loved Interstellar and Inception. I hate romcoms.",
        "domain": "movies"
    })

    assert response.status_code == 200
    data = response.json()
    assert "domain" in data
    assert "confidence" in data
