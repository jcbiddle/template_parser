from io import StringIO

import textfsm
from tabulate import tabulate


def parse_textfsm(input_text: str, template: str) -> str:
    stream = StringIO(template)
    re_table = textfsm.TextFSM(stream)
    data = re_table.ParseText(input_text)
    result = tabulate(data, tablefmt="plain", headers=re_table.header)
    print(result)
    return result
