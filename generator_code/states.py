import random


STATE_DURATION = {
    "sleeping": (4 * 60 * 60, 7 * 60 * 60),
    "resting": (15 * 60, 60 * 60),
    "walking": (5 * 60, 40 * 60),
    "running": (10 * 60, 50 * 60)
}


STATES = {
    "sleeping": {
        "heart_rate": (58, 5),
        "temperature": (36.4, 0.2),
        "accel": (0.02, 0.01)
    },
    "resting": {
        "heart_rate": (72, 6),
        "temperature": (36.7, 0.2),
        "accel": (0.08, 0.03)
    },
    "walking": {
        "heart_rate": (100, 10),
        "temperature": (36.9, 0.25),
        "accel": (0.6, 0.2)
    },
    "running": {
        "heart_rate": (145, 12),
        "temperature": (37.4, 0.3),
        "accel": (1.5, 0.35)
    }
}



TRANSITIONS = {
    "sleeping": [
        ("sleeping", 0.70),
        ("resting", 0.25),
        ("walking", 0.05)
    ],
    "resting": [
        ("resting", 0.70),
        ("walking", 0.25),
        ("sleeping", 0.05)
    ],
    "walking": [
        ("walking", 0.75),
        ("resting", 0.20),
        ("running", 0.05)
    ],
    "running": [
        ("running", 0.70),
        ("walking", 0.30)
    ]
}


def get_next_state(current_state):
    choices = TRANSITIONS[current_state]
    states = [c[0] for c in choices]
    weights = [c[1] for c in choices]
    return random.choices(states, weights=weights, k=1)[0]


def get_state_duration(state):
    min_d, max_d = STATE_DURATION[state]
    return random.randint(min_d, max_d)