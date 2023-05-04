from typing import Optional
from xml.etree.ElementTree import ParseError

from ttp import ttp


def parse_ttp(input_text: str, template: str) -> Optional[str]:
    """Parse text using a TTP template, returning the result in JSON format"""
    # print result in JSON format
    try:
        parser = ttp(data=input_text, template=template)
        parser.parse()
        results = parser.result(format="json")[0]
        return results
    except IndexError:
        return ""
    except ParseError as e:
        raise RuntimeError(e)
