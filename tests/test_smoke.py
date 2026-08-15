import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

script = importlib.import_module("script")


FEATURES = [
    "ydstogo",
    "yardline_100",
    "score_differential",
    "game_seconds_remaining",
    "posteam_timeouts_remaining",
    "defteam_timeouts_remaining",
    "is_two_minute_drill",
    "is_redzone",
]


class DummyModel:
    def __init__(self, value):
        self.value = value
        self.last_input = None

    def predict(self, values):
        self.last_input = values
        return [self.value]


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


def test_recommendation_loads_models_lazily_and_caches(monkeypatch):
    script.action_models = None
    script.features = None

    calls = []

    def fake_load(path):
        calls.append(path)
        if path.endswith("features.joblib"):
            return FEATURES
        if "go_for_it" in path:
            return DummyModel(0.4)
        if "punt" in path:
            return DummyModel(0.1)
        return DummyModel(0.2)

    monkeypatch.setattr(script.joblib, "load", fake_load)

    first_result = script.recommend_fourth_down(4, 40, 0, 300, 3, 3)
    assert first_result["recommendation"] == "Go For It"
    assert len(calls) == 4

    second_result = script.recommend_fourth_down(4, 40, 0, 300, 3, 3)
    assert second_result["recommendation"] == "Go For It"
    assert len(calls) == 4


def test_recommendation_uses_plain_row_values(monkeypatch):
    models = {
        "Go For It": DummyModel(0.7),
        "Punt": DummyModel(0.3),
        "Field Goal": DummyModel(0.4),
    }
    script.action_models = models
    script.features = FEATURES

    result = script.recommend_fourth_down(5, 35, -3, 120, 1, 2)

    assert result["recommendation"] == "Go For It"
    assert result["all_actions"][0]["epa"] == 0.7
    for model in models.values():
        assert model.last_input == [[5, 35, -3, 120, 1, 2, 1, 0]]
