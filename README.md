# 4th-Down-decider
# 4th Down Decision Engine

A machine learning model that recommends the optimal 4th-down decision (Go For It, Punt, or Field Goal) based on historical NFL play-by-play data — not just what coaches typically do, but what actually produces the best expected outcome.

## How it works

Instead of predicting *what coaches usually choose* in a given situation, this project trains three separate Random Forest models — one per action — each learning to predict the **Expected Points Added (EPA)** that action would produce given the game situation. For any live scenario, all three models are queried and the action with the highest predicted EPA is recommended.

This mirrors the approach used by public 4th-down analytics tools (e.g. the NYT's 4th Down Bot), rather than simply mimicking historical coaching behavior — which is often more conservative than optimal.

## Data

Play-by-play data is sourced from [nflverse-data](https://github.com/nflverse/nflverse-data/releases/tag/pbp), covering the 2021–2025 NFL seasons. Data is automatically downloaded and cached locally on first run.

## Features used

- `ydstogo` — yards needed for a first down
- `yardline_100` — distance from the opponent's end zone
- `score_differential` — current score differential
- `game_seconds_remaining` — time left in the game
- `posteam_timeouts_remaining` / `defteam_timeouts_remaining` — timeouts remaining for each team
- `is_two_minute_drill` — whether the play falls within a two-minute-drill window
- `is_redzone` — whether the play is inside the opponent's 20-yard line

## Setup

```bash
pip install pandas numpy scikit-learn matplotlib joblib
python fourth_down_model.py
```

On first run, the script downloads and caches multiple seasons of play-by-play data, trains and cross-validates a model for each action, and saves the trained models to `saved_models/`. Subsequent runs load the saved models directly instead of retraining.

## Usage

Run the script and enter a live game situation when prompted:

```
Enter yards to go: 2
Enter yard line: 35
Enter score differential: -3
Enter seconds remaining: 200
Enter position timeouts: 2
Enter def timeouts: 2
```

Example output:

```
[SITUATION]: 4th & 2 at the Opponent 65 Yard Line
[CONTEXT]: Score Diff: -3 | Time Left: 200s
==> RECOMMENDED DECISION: **GO FOR IT**

Expected Point Value (EPA) by action:
 * Go For It: +1.827 EPA
 * Field Goal: -0.311 EPA
 * Punt: -0.779 EPA
```

Actions that would be physically or strategically unrealistic given the inputs (e.g. a 90+ yard field goal) are automatically excluded rather than letting the model extrapolate into situations it has no real training data for.

## Model visualization

The script also exports a depth-limited image of one representative decision tree from each action's forest to `tree_exports/`, useful for understanding which factors most influence each model's predictions.

## Limitations

- This model learns from **observational** data — it only ever sees the outcome of the action a coach actually chose, never the outcome of the road not taken in that exact spot. It generalizes across similar situations, but this is not a controlled experiment.
- Predictions are only as reliable as the training data available for that region of the input space — situations far outside common historical patterns (e.g. very unusual field position/yardage combinations) are excluded by the built-in guardrails rather than guessed at.
- This tool is intended for exploratory and educational analysis, not as a substitute for professional coaching judgment.
