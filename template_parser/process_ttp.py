from ttp import ttp


def parse_ttp(input_text: str, template: str) -> str:
    """Parse text using a TTP template, returning the result in JSON format"""
    # print result in JSON format
    try:
        parser = ttp(data=input_text, template=template)
        parser.parse()
        results = parser.result(format="json")[0]
        return results
    except IndexError:
        return ""
