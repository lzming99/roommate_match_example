from datetime import datetime, timezone

def now_utc() -> datetime:
    """Return current UTC time."""
    return datetime.now(timezone.utc)