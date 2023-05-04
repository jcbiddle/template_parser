from io import StringIO

import textfsm
from tabulate import tabulate
from textfsm.parser import TextFSMTemplateError


def parse_textfsm(input_text: str, template: str) -> str:
    stream = StringIO(template)
    try:
        re_table = textfsm.TextFSM(stream)
        data = re_table.ParseText(input_text)
        result = tabulate(data, tablefmt="plain", headers=re_table.header)
        return result
    except TextFSMTemplateError as e:
        raise RuntimeError(e)
