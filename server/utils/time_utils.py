from datetime import datetime
import pytz

def get_current_timestamp(as_float=False):
    """Retorna o timestamp atual em formato ISO ou segundos."""
    now = datetime.now(pytz.UTC)
    if as_float:
        return now.timestamp()  # Segundos desde epoch
    return now.isoformat()