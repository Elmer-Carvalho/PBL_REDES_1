from datetime import datetime, timezone

def get_current_timestamp():
    """Gera um timestamp atual no formato ISO 8601 com UTC."""
    return datetime.now(timezone.utc).isoformat()