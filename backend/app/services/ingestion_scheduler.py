scheduler_state = {"enabled": False}


def toggle() -> dict:
    scheduler_state["enabled"] = not scheduler_state["enabled"]
    return scheduler_state
