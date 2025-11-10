thonimport logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class Relation:
    name: str
    age: Optional[str] = None

@dataclass
class PersonRecord:
    search_option: str
    input_given: str
    first_name: str
    last_name: str
    age: Optional[str] = None
    born: Optional[str] = None
    lives_in: Optional[str] = None
    street_address: Optional[str] = None
    address_locality: Optional[str] = None
    address_region: Optional[str] = None
    postal_code: Optional[str] = None
    county_name: Optional[str] = None
    emails: List[str] = field(default_factory=list)
    phones: List[Dict[str, Optional[str]]] = field(default_factory=list)
    previous_addresses: List[Dict[str, Optional[str]]] = field(default_factory=list)
    relatives: List[Relation] = field(default_factory=list)
    associates: List[Relation] = field(default_factory=list)
    person_link: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the record into the JSON structure described in the README."""
        result: Dict[str, Any] = {
            "Search Option": self.search_option,
            "Input Given": self.input_given,
            "First Name": self.first_name,
            "Last Name": self.last_name,
        }

        if self.age is not None:
            result["Age"] = self.age
        if self.born is not None:
            result["Born"] = self.born
        if self.lives_in is not None:
            result["Lives in"] = self.lives_in
        if self.street_address is not None:
            result["Street Address"] = self.street_address
        if self.address_locality is not None:
            result["Address Locality"] = self.address_locality
        if self.address_region is not None:
            result["Address Region"] = self.address_region
        if self.postal_code is not None:
            result["Postal Code"] = self.postal_code
        if self.county_name is not None:
            result["County Name"] = self.county_name

        # Emails
        for idx, email in enumerate(self.emails, start=1):
            result[f"Email-{idx}"] = email

        # Phones
        for idx, phone in enumerate(self.phones, start=1):
            number = phone.get("number")
            if number:
                result[f"Phone-{idx}"] = number
            type_ = phone.get("type")
            if type_:
                result[f"Phone-{idx} Type"] = type_
            provider = phone.get("provider")
            if provider:
                result[f"Phone-{idx} Provider"] = provider

        # Previous addresses
        if self.previous_addresses:
            result["Previous Addresses"] = self.previous_addresses

        # Relatives
        if self.relatives:
            result["Relatives"] = [
                {"Name": rel.name, "Age": rel.age} for rel in self.relatives
            ]

        # Associates
        if self.associates:
            result["Associates"] = [
                {"Name": rel.name, "Age": rel.age} for rel in self.associates
            ]

        # Person link
        if self.person_link:
            result["Person Link"] = self.person_link

        return result

class IdentityExtractor:
    """
    A simple in-memory "scraper" that simulates skip tracing.

    In a production system this would issue HTTP requests, parse HTML/JSON,
    and map it into the PersonRecord structure. For this demo we keep a small,
    deterministic dataset so the project is fully runnable without external
    dependencies or network access.
    """

    def __init__(self) -> None:
        self._records = self._build_static_dataset()
        self._by_name = {
            self._normalize_key(rec["name_key"]): rec for rec in self._records
        }
        self._by_phone = {
            self._normalize_key(phone): rec
            for rec in self._records
            for phone in rec.get("phone_keys", [])
        }
        logger.debug(
            "IdentityExtractor initialized with %d static record(s)", len(self._records)
        )

    @staticmethod
    def _normalize_key(value: str) -> str:
        return "".join(value.lower().split())

    @staticmethod
    def _build_static_dataset() -> List[Dict[str, Any]]:
        """
        Build an in-memory dataset that mimics external skip-trace results.

        You can extend this with your own fixtures or hook it up to real data.
        """
        return [
            {
                # Name-based record used in the README example
                "name_key": "James E Whitsitt",
                "phone_keys": ["(214) 534-2474"],
                "first_name": "James",
                "last_name": "Whitsitt",
                "age": "76",
                "born": "February 1949",
                "lives_in": "1727 Summerlin Pl Jeffersonville IN 47130",
                "street_address": "1727 Summerlin Pl",
                "address_locality": "Jeffersonville",
                "address_region": "IN",
                "postal_code": "47130",
                "county_name": "Clark County",
                "emails": ["goldiewhitsitt@hotmail.com"],
                "phones": [
                    {
                        "number": "(214) 534-2474",
                        "type": "Wireless",
                        "provider": "New Cingular Wireless PCS LLC - IL",
                    }
                ],
                "previous_addresses": [
                    {
                        "streetAddress": "928 Meadowcove Cir",
                        "addressLocality": "Garland",
                        "addressRegion": "TX",
                        "postalCode": "75043",
                        "county": "Dallas County",
                        "timespan": "Recorded July 1989",
                    }
                ],
                "relatives": [
                    {"Name": "Janice Whitsitt", "Age": "79"},
                    {"Name": "Goldie Whitsitt", "Age": "75"},
                ],
                "associates": [
                    {"Name": "Lola Sonnenberg", "Age": "104"},
                ],
                "person_link": "https://www.fastpeoplesearch.com/james-whitsitt_id_G-5782184243798810449",
            },
            {
                # A second record mainly to demonstrate phone-based search
                "name_key": "Sarah L Carter",
                "phone_keys": ["+1 (305) 555-0199", "305-555-0199"],
                "first_name": "Sarah",
                "last_name": "Carter",
                "age": "42",
                "born": "May 1983",
                "lives_in": "901 Ocean Dr Miami FL 33139",
                "street_address": "901 Ocean Dr",
                "address_locality": "Miami",
                "address_region": "FL",
                "postal_code": "33139",
                "county_name": "Miami-Dade County",
                "emails": [
                    "sarah.carter@example.com",
                    "s.carter.work@example.org",
                ],
                "phones": [
                    {
                        "number": "+1 (305) 555-0199",
                        "type": "Wireless",
                        "provider": "Verizon Wireless",
                    },
                    {
                        "number": "(305) 555-0177",
                        "type": "Landline",
                        "provider": "AT&T",
                    },
                ],
                "previous_addresses": [
                    {
                        "streetAddress": "1001 Sunset Blvd",
                        "addressLocality": "Los Angeles",
                        "addressRegion": "CA",
                        "postalCode": "90012",
                        "county": "Los Angeles County",
                        "timespan": "Recorded March 2010",
                    }
                ],
                "relatives": [
                    {"Name": "Michael Carter", "Age": "45"},
                    {"Name": "Emily Carter", "Age": "15"},
                ],
                "associates": [
                    {"Name": "Luis Rodriguez", "Age": "39"},
                ],
                "person_link": "https://example.com/person/sarah-l-carter",
            },
        ]

    def _make_person_record(
        self, search_option: str, input_given: str, raw: Dict[str, Any]
    ) -> PersonRecord:
        relatives = [
            Relation(name=item.get("Name", ""), age=item.get("Age"))
            for item in raw.get("relatives", [])
            if item.get("Name")
        ]
        associates = [
            Relation(name=item.get("Name", ""), age=item.get("Age"))
            for item in raw.get("associates", [])
            if item.get("Name")
        ]

        record = PersonRecord(
            search_option=search_option,
            input_given=input_given,
            first_name=raw["first_name"],
            last_name=raw["last_name"],
            age=raw.get("age"),
            born=raw.get("born"),
            lives_in=raw.get("lives_in"),
            street_address=raw.get("street_address"),
            address_locality=raw.get("address_locality"),
            address_region=raw.get("address_region"),
            postal_code=raw.get("postal_code"),
            county_name=raw.get("county_name"),
            emails=list(raw.get("emails", [])),
            phones=list(raw.get("phones", [])),
            previous_addresses=list(raw.get("previous_addresses", [])),
            relatives=relatives,
            associates=associates,
            person_link=raw.get("person_link"),
        )

        logger.debug("Built PersonRecord from raw data for '%s'", input_given)
        return record

    def lookup(self, search_option: str, input_value: str) -> PersonRecord:
        """
        Lookup a person using the given search option and input value.

        Supported search options (case-insensitive) include:
            - "Name Search"
            - "Phone Search"
            - any string; we do a best-effort match
        """
        normalized_input = self._normalize_key(input_value)
        normalized_option = search_option.strip().lower()

        logger.info(
            "Looking up identity for '%s' using search option '%s'",
            input_value,
            search_option,
        )

        raw: Optional[Dict[str, Any]] = None

        if "phone" in normalized_option:
            raw = self._by_phone.get(normalized_input)
        elif "name" in normalized_option:
            raw = self._by_name.get(normalized_input)

        # Fallback: try both maps if we didn't find a record yet
        if raw is None:
            raw = self._by_name.get(normalized_input) or self._by_phone.get(
                normalized_input
            )

        if raw is None:
            msg = (
                f"No matching record found for input '{input_value}' "
                f"with option '{search_option}'"
            )
            logger.error(msg)
            raise LookupError(msg)

        return self._make_person_record(search_option, input_value, raw)