import statistics


def _clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def _normalize(value, min_value, max_value):
    if max_value == min_value:
        return 0.0
    return _clamp((value - min_value) / (max_value - min_value))


def _build_game_narrative(anxiety, mood, stress, avg_rt, accuracy, cpm):
    wellbeing = (1 - anxiety + mood + (1 - stress)) / 3

    if anxiety > 0.6:
        primary_emotion = "Anxious"
    elif stress > 0.6:
        primary_emotion = "Stressed"
    elif mood > 0.65:
        primary_emotion = "Engaged"
    elif mood < 0.35:
        primary_emotion = "Low"
    elif accuracy > 0.7:
        primary_emotion = "Focused"
    else:
        primary_emotion = "Mixed"

    summary_parts = []
    if anxiety > 0.5:
        summary_parts.append(f"elevated tension ({anxiety:.0%})")
    if stress > 0.5:
        summary_parts.append(f"noticeable stress load ({stress:.0%})")
    if mood > 0.6:
        summary_parts.append(f"strong engagement ({mood:.0%})")
    elif mood < 0.4:
        summary_parts.append(f"reduced emotional energy ({mood:.0%})")

    if summary_parts:
        summary = (
            "Your gameplay patterns suggest "
            + ", ".join(summary_parts)
            + ". "
            + "Reaction timing and click behavior indicate how your mind was regulating focus and pressure in real time."
        )
    else:
        summary = (
            "Your gameplay reflects a mixed but manageable emotional pattern. "
            "You stayed reasonably responsive while showing normal variation in pace and focus."
        )

    details = []
    if anxiety > 0.55:
        details.append("Reaction timing varied significantly, which often appears when attention feels restless or over-alert.")
    if stress > 0.55:
        details.append("Accuracy and pace suggest cognitive load was higher than comfortable levels.")
    if mood > 0.6:
        details.append("Consistent target engagement indicates active motivation and adaptive focus.")
    if mood < 0.4:
        details.append("Lower sustained engagement hints at emotional fatigue or reduced drive.")
    if avg_rt > 700:
        details.append("Slower average response speed may reflect mental heaviness, caution, or depletion.")
    if cpm > 100:
        details.append("Very high click tempo suggests urgency and possible overactivation.")

    if len(details) < 3:
        details.extend([
            "Your interaction rhythm still showed moments of control and adjustment.",
            "The pattern suggests your state is responsive to short guided regulation exercises.",
        ])

    if stress > 0.6 or anxiety > 0.6:
        mental_state = (
            "Performance suggests a high-arousal state with fluctuating attention control. "
            "You are likely operating under pressure while trying to maintain task focus."
        )
    elif mood > 0.65 and accuracy > 0.7:
        mental_state = (
            "Performance indicates a steady, task-engaged state with healthy cognitive control. "
            "You were able to sustain focus without excessive volatility."
        )
    else:
        mental_state = (
            "Performance indicates a moderate state with mixed arousal and focus stability. "
            "You are functioning, but regulation support could improve consistency."
        )

    if anxiety > 0.6:
        body_connection = (
            "This pattern is often paired with shallow breathing, jaw or shoulder tension, "
            "and a fast internal pace."
        )
    elif stress > 0.6:
        body_connection = (
            "This profile can align with mental fatigue, muscle tightness, and reduced recovery between efforts."
        )
    elif mood > 0.6:
        body_connection = (
            "Your body likely supported this session with relatively balanced breathing and sustained alertness."
        )
    else:
        body_connection = (
            "Your body state appears mixed, with signs of effort and normal fluctuation in energy and control."
        )

    if accuracy > 0.7:
        strength_noted = "You showed strong task persistence and adaptive correction while the game evolved."
    elif cpm > 70:
        strength_noted = "You remained actively engaged throughout the session, which reflects solid effort and presence."
    else:
        strength_noted = "Completing the session itself shows commitment to self-awareness and proactive emotional care."

    if wellbeing > 0.7:
        garden_description = (
            "Your garden feels bright and open, with clear light, stable air, and flowers standing upright in full color."
        )
    elif wellbeing > 0.5:
        garden_description = (
            "Your garden shows moving clouds with steady sunlight breaking through, and healthy growth returning across the paths."
        )
    elif wellbeing > 0.3:
        garden_description = (
            "Your garden is overcast and wind-touched, yet rooted plants continue to hold and recover between gusts."
        )
    else:
        garden_description = (
            "Your garden is under a dense storm layer, but the roots are still alive and capable of rebuilding calm."
        )

    return {
        "summary": summary,
        "primary_emotion": primary_emotion,
        "emotional_details": details[:3],
        "mental_state": mental_state,
        "body_connection": body_connection,
        "strength_noted": strength_noted,
        "garden_description": garden_description,
    }


def analyze_game_metrics(game_data: dict) -> dict:
    reaction_times = [
        float(value)
        for value in game_data.get("reaction_times", [])
        if isinstance(value, (int, float))
    ]

    correct_pops = int(game_data.get("correct_pops", 0) or 0)
    empty_clicks = int(game_data.get("empty_clicks", 0) or 0)
    total_clicks = int(game_data.get("total_clicks", 0) or 0)
    total_seconds = int(game_data.get("total_seconds", 0) or 0)
    pause_count = int(game_data.get("pause_count", 0) or 0)
    accuracy_trend = float(game_data.get("accuracy_trend", 0.0) or 0.0)

    total_clicks = max(total_clicks, 0)
    total_seconds = max(total_seconds, 1)
    correct_pops = max(correct_pops, 0)
    empty_clicks = max(empty_clicks, 0)
    pause_count = max(pause_count, 0)

    accuracy = _clamp(correct_pops / max(total_clicks, 1))
    miss_ratio = _clamp(empty_clicks / max(total_clicks, 1))

    avg_rt = statistics.mean(reaction_times) if reaction_times else 550.0
    rt_variance = statistics.stdev(reaction_times) if len(reaction_times) > 1 else 80.0
    cpm = (total_clicks / total_seconds) * 60.0

    rt_variance_norm = _normalize(rt_variance, 50, 400)
    miss_ratio_norm = _normalize(miss_ratio, 0, 0.6)
    cpm_norm = _normalize(cpm, 30, 120)

    anxiety = _clamp(
        (rt_variance_norm * 0.40) +
        (miss_ratio_norm * 0.35) +
        (cpm_norm * 0.25)
    )

    trend_down_norm = _normalize(-accuracy_trend, -0.3, 0.3)
    avg_rt_norm = _normalize(avg_rt, 300, 900)

    stress = _clamp(
        ((1 - accuracy) * 0.50) +
        (trend_down_norm * 0.30) +
        (avg_rt_norm * 0.20)
    )

    engagement = 1.0 - _normalize(pause_count, 0, 8)
    trend_up_norm = _normalize(accuracy_trend, -0.3, 0.3)

    mood = _clamp(
        (accuracy * 0.40) +
        (engagement * 0.35) +
        (trend_up_norm * 0.25)
    )

    analysis = _build_game_narrative(anxiety, mood, stress, avg_rt, accuracy, cpm)

    return {
        "anxiety": round(anxiety, 2),
        "mood": round(mood, 2),
        "stress": round(stress, 2),
        "analysis": analysis,
    }
