playbooks = {}


def save(playbook: dict) -> None:
    playbooks[playbook["incident_id"]] = playbook


def get(incident_id: str):
    return playbooks.get(incident_id)
