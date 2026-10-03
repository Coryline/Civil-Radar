import re
from typing import Any


class PublicSourceHarness:
    @staticmethod
    def clean_text(value: Any) -> str:
        if value is None:
            return ""
        return re.sub(r"<.*?>", " ", str(value)).strip()
