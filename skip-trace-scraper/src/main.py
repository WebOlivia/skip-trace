thonimport json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List

from utils.data_parser import load_queries, SearchQuery
from utils.formatter import write_results, pretty_print_result
from extractors.identity_extractor import IdentityExtractor
from extractors.relations_extractor import RelationsExtractor

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS_PATH = ROOT_DIR / "src" / "config" / "settings.json"

def load_settings(settings_path: Path) -> Dict[str, Any]:
    if not settings_path.exists():
        raise FileNotFoundError(f"Settings file not found at: {settings_path}")

    try:
        with settings_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in settings file: {exc}") from exc

    required_keys = ["input_file", "output_file", "max_workers", "log_level"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise KeyError(f"Missing required settings: {', '.join(missing)}")

    return data

def configure_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    logging.debug("Logging configured at %s level", level_name)

def process_query(
    query: SearchQuery,
    identity_extractor: IdentityExtractor,
    relations_extractor: RelationsExtractor,
) -> Dict[str, Any]:
    logger = logging.getLogger("process_query")
    logger.debug("Processing query: %s", query)

    person_record = identity_extractor.lookup(query.search_option, query.input_value)
    enriched_record = relations_extractor.enrich_relations(person_record)
    result_dict = enriched_record.to_dict()

    logger.info(
        "Processed query '%s' (%s) successfully",
        query.input_value,
        query.search_option,
    )
    return result_dict

def main() -> int:
    logger = logging.getLogger("main")

    try:
        settings = load_settings(DEFAULT_SETTINGS_PATH)
    except Exception as exc:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        )
        logging.error("Failed to load settings: %s", exc)
        return 1

    configure_logging(settings.get("log_level", "INFO"))

    input_path = ROOT_DIR / settings["input_file"]
    output_path = ROOT_DIR / settings["output_file"]
    max_workers = int(settings.get("max_workers", 4))

    logger.info("Skip Trace Scraper starting up")
    logger.debug("Root directory: %s", ROOT_DIR)
    logger.debug("Input path: %s", input_path)
    logger.debug("Output path: %s", output_path)
    logger.debug("Max workers: %d", max_workers)

    try:
        queries = load_queries(input_path)
    except Exception as exc:
        logger.error("Failed to load input queries: %s", exc)
        return 1

    if not queries:
        logger.warning("No queries found in input file. Exiting.")
        write_results([], output_path)
        return 0

    identity_extractor = IdentityExtractor()
    relations_extractor = RelationsExtractor()

    results: List[Dict[str, Any]] = []
    errors: List[str] = []

    logger.info("Processing %d queries using up to %d workers", len(queries), max_workers)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_query = {
            executor.submit(
                process_query,
                query,
                identity_extractor,
                relations_extractor,
            ): query
            for query in queries
        }

        for future in as_completed(future_to_query):
            query = future_to_query[future]
            try:
                result = future.result()
                results.append(result)
                pretty_print_result(result)
            except Exception as exc:
                msg = f"Failed to process query '{query.input_value}' ({query.search_option}): {exc}"
                logger.error(msg)
                errors.append(msg)

    write_results(results, output_path)

    logger.info("Processing complete: %d success, %d failed", len(results), len(errors))

    if errors:
        logger.warning("Some queries failed to process. See logs for details.")

    return 0

if __name__ == "__main__":
    sys.exit(main())