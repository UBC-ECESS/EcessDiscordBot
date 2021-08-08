from typing import Dict, Any, Set
import json
import os

SECRETS_DIR: str = "secrets"
SECRETS_PATH: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", SECRETS_DIR
)

RESERVED_FILENAMES: Set[str] = {"token.txt"}


def _is_valid_filename(filename: str) -> None:
    if filename in RESERVED_FILENAMES:
        raise ValueError(
            f"Given filename {filename} conflicts with reserved filenames."
        )


def write_json(filename: str, payload: Dict[Any, Any]) -> None:
    """Wrapper around writing a JSON payload to a file in the secrets directory."""
    _is_valid_filename(filename)
    with open(os.path.join(SECRETS_PATH, filename), "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def read_json(filename: str) -> Dict[Any, Any]:
    """Wrapper around reading a JSON file in the secrets directory."""
    _is_valid_filename(filename)
    try:
        with open(os.path.join(SECRETS_PATH, filename), "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        default_payload = {}
        write_json(filename, default_payload)
        return default_payload