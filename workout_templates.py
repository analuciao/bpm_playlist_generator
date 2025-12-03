# workout_templates.py
"""Common interval workout patterns."""

WORKOUTS = {
    "beginner_30min": [
        ("warmup", 3),
        ("steady_state", 6),
        ("push_pace", 2),
        ("steady_state", 2),
    ],
    
    "hiit_intervals": [
        ("warmup", 2),
        ("push_pace", 2),
        ("steady_state", 2),
        ("sprint", 1),
        ("steady_state", 2),
        ("sprint", 1),
        ("warmup", 1),  # cooldown
    ],
    
    "progressive_build": [
        ("warmup", 2),
        ("steady_state", 3),
        ("push_pace", 3),
        ("sprint", 2),
        ("push_pace", 1),
        ("warmup", 1), 
    ],
}