
def switch_tenant(user: dict, tenant_id: str) -> dict:
    user["tenant_id"] = tenant_id
    return user
