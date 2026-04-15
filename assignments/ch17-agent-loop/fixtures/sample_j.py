from datetime import datetime, timezone

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def format_iso(dt: datetime) -> str:
    return dt.isoformat()

def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s)
