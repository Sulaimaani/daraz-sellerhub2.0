import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def check_unknown_fields(payload: Dict[str, Any], known_fields: List[str], resource_name: str) -> None:
    """
    Checks for any fields in the payload that are not in the known_fields list.
    Logs them to help discover schema drift.
    """
    payload_keys = set(payload.keys())
    known_keys = set(known_fields)
    unknown_keys = payload_keys - known_keys
    
    if unknown_keys:
        # TODO: Implement a rate-limiting filter for this logger so it only logs once per field name per day.
        for key in unknown_keys:
            logger.warning(f"Unknown field '{key}' encountered in {resource_name} payload.")

def safe_decimal(value: Any) -> float:
    try:
        return float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        return 0.0

def safe_int(value: Any) -> int:
    try:
        return int(value) if value is not None else 0
    except (ValueError, TypeError):
        return 0

def safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'y')
    if isinstance(value, int):
        return value > 0
    return False
