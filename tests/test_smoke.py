import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import script


def test_app_exists():
    assert script.app is not None


def test_core_routes_registered():
    routes = {rule.rule for rule in script.app.url_map.iter_rules()}
    assert "/" in routes
    assert "/calculate" in routes


def test_home_endpoint_smoke():
    client = script.app.test_client()
    response = client.get("/")
    assert response.status_code == 200
