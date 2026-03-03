from app.services.pipeline_orchestrator import process_log


async def ingest_manual(tenant_id: str, source: str, raw_log: str, asset_criticality: float) -> dict:
    return await process_log(tenant_id, source, raw_log, asset_criticality)
