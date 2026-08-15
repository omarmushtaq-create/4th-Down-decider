import joblib
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)

MODEL_DIR = "saved_models"

MODEL_PATHS = {
    action: f"{MODEL_DIR}/{action.lower().replace(' ', '_')}_model.joblib"
    for action in ["Go For It", "Punt", "Field Goal"]
}

FEATURES_PATH = f"{MODEL_DIR}/features.joblib"

action_models = None
features = None


def load_saved_models():
    global action_models, features

    if action_models is not None and features is not None:
        return

    try:
        action_models = {
            action: joblib.load(path)
            for action, path in MODEL_PATHS.items()
        }
        features = joblib.load(FEATURES_PATH)
        print("Saved models loaded successfully.")
    except FileNotFoundError as error:
        print(f"ERROR: Could not find a model file: {error}")
        action_models = {}
        features = []


def recommend_fourth_down(
    ydstogo,
    yardline_100,
    score_differential,
    seconds_remaining,
    pos_timeouts,
    def_timeouts,
):
    """
    Predict the expected EPA for each realistic fourth-down decision
    and return the best option.
    """

    load_saved_models()

    if not action_models:
        return {
            "error": "The trained models could not be loaded."
        }

    is_two_minute_drill = int(
        seconds_remaining <= 120
        or 1680 <= seconds_remaining <= 1800
    )
    is_redzone = int(yardline_100 <= 20)

    feature_values = {
        "ydstogo": ydstogo,
        "yardline_100": yardline_100,
        "score_differential": score_differential,
        "seconds_remaining": seconds_remaining,
        "game_seconds_remaining": seconds_remaining,
        "pos_timeouts": pos_timeouts,
        "posteam_timeouts_remaining": pos_timeouts,
        "def_timeouts": def_timeouts,
        "defteam_timeouts_remaining": def_timeouts,
        "is_two_minute_drill": is_two_minute_drill,
        "is_redzone": is_redzone,
    }

    try:
        situation = [[feature_values[feature] for feature in features]]
    except KeyError:
        return {
            "error": "The trained model is missing expected features."
        }

    predicted_values = {}

    for action, model in action_models.items():
        if action == "Field Goal" and yardline_100 > 40:
            continue

        if action == "Punt" and yardline_100 < 35:
            continue

        if action == "Go For It" and ydstogo > 10:
            continue

        prediction = float(model.predict(situation)[0])
        predicted_values[action] = prediction

    if not predicted_values:
        return {
            "error": "No realistic action was modeled for this situation."
        }

    sorted_actions = sorted(
        predicted_values.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    best_action, best_value = sorted_actions[0]
    margin = None

    if len(sorted_actions) > 1:
        margin = best_value - sorted_actions[1][1]

    return {
        "recommendation": best_action,
        "best_epa": best_value,
        "margin": margin,
        "all_actions": [
            {"action": action, "epa": value}
            for action, value in sorted_actions
        ],
    }


@app.route("/")
def home():
    return send_file("index.html")


@app.route("/style.css")
def style():
    return send_file("style.css")


@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()

        ydstogo = int(data["ydstogo"])
        yardline_100 = int(data["yardline_100"])
        your_points = int(data["your_points"])
        opponent_points = int(data["opponent_points"])
        seconds_remaining = int(data["seconds_remaining"])
        pos_timeouts = int(data["pos_timeouts"])
        def_timeouts = int(data["def_timeouts"])

        score_differential = your_points - opponent_points

        if ydstogo < 1:
            return jsonify({"error": "Distance to go must be at least 1."}), 400

        if not 1 <= yardline_100 <= 99:
            return jsonify({"error": "Yard line must be between 1 and 99."}), 400

        if not 0 <= seconds_remaining <= 3600:
            return (
                jsonify(
                    {"error": "Seconds remaining must be between 0 and 3600."}
                ),
                400,
            )

        if not 0 <= pos_timeouts <= 3:
            return jsonify({"error": "Your timeouts must be between 0 and 3."}), 400

        if not 0 <= def_timeouts <= 3:
            return jsonify({"error": "Opponent timeouts must be between 0 and 3."}), 400

        result = recommend_fourth_down(
            ydstogo,
            yardline_100,
            score_differential,
            seconds_remaining,
            pos_timeouts,
            def_timeouts,
        )

        if "error" in result:
            return jsonify(result), 500

        return jsonify(result)

    except KeyError:
        return jsonify({"error": "Missing required value."}), 400
    except ValueError:
        return jsonify({"error": "Please enter valid numbers."}), 400
    except Exception:
        print("Unexpected server error.")
        return jsonify({"error": "An unexpected server error occurred."}), 500


if __name__ == "__main__":
    app.run()
