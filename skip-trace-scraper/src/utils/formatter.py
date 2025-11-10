thonimport json
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

def write_results(results: List[Dict[str, Any]], output_path: Path) -> None:
    """
    Write the aggregated results to the output JSON file.

    The directory is created if it does not exist.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.debug("Writing %d result(s) to %s", len(results), output_path)

    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
    except OSError as exc:
        logger.error("Failed to write results to %s: %s", output_path, exc)
        raise

def pretty_print_result(result: Dict[str, Any]) -> None:
    """
    Print a single result in a human-friendly JSON format to stdout.

    This is useful when running the script interactively.
    """
    try:
        formatted = json.dumps(result, indent=4, ensure_ascii=False)
    except TypeError:
        # As a fallback, convert non-serializable objects to string
        def default(obj: Any) -> str:
            return str(obj)

        formatted = json.dumps(result, indent=4, ensure_ascii=False, default=default)

    print("\n=== Skip Trace Result ===")
    print(formatted)
    print("=========================\n")