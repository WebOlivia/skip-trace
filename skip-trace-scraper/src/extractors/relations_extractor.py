thonimport logging
from typing import List

from .identity_extractor import PersonRecord, Relation

logger = logging.getLogger(__name__)

class RelationsExtractor:
    """
    Performs lightweight enrichment and normalization of relations data.

    In a production-grade system this could:
      - Cross-check relatives/associates against additional data sources
      - Infer new connections
      - Resolve duplicates across multiple profiles
    For this runnable demo we focus on data hygiene, ordering, and deduplication.
    """

    @staticmethod
    def _deduplicate_relations(relations: List[Relation]) -> List[Relation]:
        seen = set()
        unique: List[Relation] = []

        for rel in relations:
            key = (rel.name.strip().lower(), (rel.age or "").strip())
            if key in seen:
                continue
            seen.add(key)
            unique.append(rel)

        return unique

    @staticmethod
    def _sort_relations(relations: List[Relation]) -> List[Relation]:
        # Sort by numeric age (if available), then by name
        def sort_key(rel: Relation):
            try:
                age_val = int(rel.age) if rel.age is not None else -1
            except ValueError:
                age_val = -1
            return (-age_val, rel.name.lower())

        return sorted(relations, key=sort_key)

    def enrich_relations(self, record: PersonRecord) -> PersonRecord:
        """
        Clean and enrich relations data attached to a PersonRecord.

        - Deduplicates relatives and associates
        - Sorts them by age (descending) then by name
        - Normalizes whitespace in names and ages
        """
        logger.debug(
            "Enriching relations for %s %s",
            record.first_name,
            record.last_name,
        )

        # Normalize whitespace
        def normalize(rel: Relation) -> Relation:
            rel.name = " ".join(rel.name.split())
            if rel.age is not None:
                rel.age = rel.age.strip()
            return rel

        record.relatives = [normalize(rel) for rel in record.relatives]
        record.associates = [normalize(rel) for rel in record.associates]

        # Deduplicate and sort
        record.relatives = self._sort_relations(
            self._deduplicate_relations(record.relatives)
        )
        record.associates = self._sort_relations(
            self._deduplicate_relations(record.associates)
        )

        logger.info(
            "Relations enrichment complete for %s %s: %d relatives, %d associates",
            record.first_name,
            record.last_name,
            len(record.relatives),
            len(record.associates),
        )

        return record