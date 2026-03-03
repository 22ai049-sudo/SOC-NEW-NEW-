ROLE_LEVEL = {"Analyst": 1, "Manager": 2, "Admin": 3}


def enforce_role(user: dict, min_role: str) -> bool:
    return ROLE_LEVEL.get(user.get("role", "Analyst"), 0) >= ROLE_LEVEL.get(min_role, 0)
