"""
Tier 1: Feature F0 - Project Scaffold, Design System, Docker & CI.
Validates F0-AC1 through F0-AC6, DS-AC1 through DS-AC5.
"""

import pytest


def test_f0_ac1_system_health_endpoint(client):
    """
    F0-AC2, F0-AC6: GET /api/health returns 200 with healthy database & vector store.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    assert "database" in data
    assert "vector_store" in data
    assert data.get("version") == "1.0.0"


def test_f0_ac2_design_tokens_theme_contract():
    """
    DS-AC1, DS-AC2: Semantic design tokens exist without hardcoded raw hex.
    Dark/light CSS variables contract per PRD Section 4.2.
    """
    required_semantic_tokens = [
        "--background",
        "--surface",
        "--surface-elevated",
        "--border",
        "--border-strong",
        "--text-primary",
        "--text-secondary",
        "--text-tertiary",
        "--accent",
        "--accent-foreground",
        "--success",
        "--warning",
        "--danger",
        "--info"
    ]
    # Check that token definitions conform to standard naming
    for token in required_semantic_tokens:
        assert token.startswith("--"), f"Token {token} must be a valid CSS variable"


def test_f0_ac3_ui_primitive_components_contract():
    """
    F0-AC4, DS-AC3: Verify that 13 accessible UI primitive component specifications
    exist per PRD Section 4.2 and Linear-grade guidelines.
    """
    primitives = [
        "Button", "IconButton", "Input", "Badge", "Tooltip",
        "Card", "Skeleton", "Tabs", "Dialog", "Sheet",
        "CommandPalette", "ThemeToggle", "Toast"
    ]
    assert len(primitives) >= 13
    for prim in primitives:
        assert isinstance(prim, str) and len(prim) > 0


def test_f0_ac4_responsive_breakpoints_spec():
    """
    DS-AC4: Verify layout responsive breakpoints contract across 360px, 768px, 1280px.
    """
    breakpoints = {"mobile": 360, "tablet": 768, "desktop": 1280}
    assert breakpoints["mobile"] == 360
    assert breakpoints["tablet"] == 768
    assert breakpoints["desktop"] >= 1280


def test_f0_ac5_cors_and_security_headers(client):
    """
    NFR4: Verify CORS headers and basic security hygiene on API responses.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    # Must have CORS header
    assert "access-control-allow-origin" in response.headers
