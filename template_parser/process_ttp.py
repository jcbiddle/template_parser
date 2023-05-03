from typing import Optional
from xml.etree.ElementTree import ParseError

from ttp import ttp


def parse_ttp(input_text: str, template: str) -> Optional[str]:
    """Parse text using a TTP template, returning the result in JSON format"""
    parser = ttp(data=input_text, template=template)
    parser.parse()

    # print result in JSON format
    try:
        results = parser.result(format="json")[0]
        return results
    except IndexError:
        return ""
    except ParseError:
        return None
