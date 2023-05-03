import logging.config
from textwrap import dedent
from xml.etree.ElementTree import ParseError

import dash_bootstrap_components as dbc
from dash import html, Dash, Input, Output, dcc, State, ALL
from dash.exceptions import PreventUpdate
from textfsm.parser import TextFSMTemplateError

from template_parser.process_textfsm import parse_textfsm
from template_parser.process_ttp import parse_ttp

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
    }
)
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

TEMPLATE_LANGUAGES = {
    "ttp": {"name": "TTP"},
    "textfsm": {"name": "TextFSM"},
}


def build_page_content(template_language: str):
    if template_language not in TEMPLATE_LANGUAGES:
        raise ValueError(f"Unrecognised language {template_language}")
    data = TEMPLATE_LANGUAGES[template_language]
    language_name = data.get("name", template_language)
    return html.Div(
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        dbc.Textarea(
                            id={"type": "raw-input", "index": template_language},
                            placeholder=f"Enter raw text",
                            style={"height": "100%", "resize": "None"},
                            draggable=False,
                            persistence=True,
                            persistence_type="session",
                        ),
                        dcc.Clipboard(
                            target_id={"type": "raw-input", "index": template_language},
                            title="copy",
                            style={
                                "position": "absolute",
                                "top": 0,
                                "right": 20,
                                "fontSize": 20,
                            },
                        ),
                    ],
                        style={"position": "relative", "height": "100%"}
                    )
                ),

                dbc.Col(
                    html.Div(
                        [dbc.Textarea(
                            id={"type": "input", "index": template_language},
                            placeholder=f"Enter {language_name} template",
                            style={"height": "100%", "resize": "None"},
                            draggable=False,
                            persistence=True,
                            persistence_type="session",
                        ),
                            dcc.Clipboard(
                                target_id={"type": "input", "index": template_language},
                                title="copy",
                                style={
                                    "position": "absolute",
                                    "top": 0,
                                    "right": 20,
                                    "fontSize": 20,
                                },
                            ),
                        ],
                        style={"position": "relative", "height": "100%"}
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        html.Div([
                            dcc.Markdown(
                                children="Results will appear here",
                                id={"type": "output", "index": template_language},
                                style={
                                    "resize": "None",
                                    "white-space": "pre",
                                },
                            ),
                            dcc.Clipboard(
                                target_id={"type": "input", "index": template_language},
                                title="copy",
                                style={
                                    "position": "absolute",
                                    "top": 0,
                                    "right": 20,
                                    "fontSize": 20,
                                },
                            ),
                        ],
                            style={"position": "relative", "height": "100%", "class": "form-control"}
                        ),
                        style={"height": "100%", "padding": "10px"}
                    )
                ),
            ],
            style={"height": "90vh"},
        ),
    )


tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(
                    label=TEMPLATE_LANGUAGES[language].get("name", language),
                    tab_id=f"tab-{language}",
                )
                for language in TEMPLATE_LANGUAGES
            ],
            id="tabs",
            persistence=True,
            persistence_type="session",
        ),
    ]
)


@app.callback(Output("content", "children"), Input("tabs", "active_tab"))
def switch_tab(at: str):
    language = at.split("-")[-1]
    return build_page_content(language)


@app.callback(
    Output({"type": "output", "index": "ttp"}, "children"),
    Output({"type": "input", "index": "ttp"}, "invalid"),
    Input({"type": "input", "index": "ttp"}, "value"),
    Input({"type": "raw-input", "index": "ttp"}, "value"),
    State({"type": "output", "index": "ttp"}, "children"),
)
def process_ttp(template_text, raw_text, existing_result):
    if template_text is None or raw_text is None:
        raise PreventUpdate
    try:
        result = parse_ttp(raw_text, template_text)
    except ParseError:
        return existing_result, True

    if not result:
        return existing_result, False

    result = dedent(
        f"""\
```json
{result}
```
    """
    )
    return result, False


@app.callback(
    Output({"type": "output", "index": "textfsm"}, "children"),
    Output({"type": "input", "index": "textfsm"}, "invalid"),
    Input({"type": "input", "index": "textfsm"}, "value"),
    Input({"type": "raw-input", "index": "textfsm"}, "value"),
    State({"type": "output", "index": "textfsm"}, "children"),
)
def process_textfsm(template_text, raw_text, existing_result):
    if template_text is None or raw_text is None:
        raise PreventUpdate
    try:
        result = parse_textfsm(raw_text, template_text)
        return result, False
    except TextFSMTemplateError:
        return existing_result, True


@app.callback(Output({"type": "input", "index": ALL}, "value", allow_duplicate=True),
              Output({"type": "raw-input", "index": ALL}, "value", allow_duplicate=True),
              Input("btn-clear-text", 'n_clicks'),
              prevent_initial_call=True
              )
def clear_templates(_):
    return [""], [""]


def serve_layout():
    return dbc.Container(
        [
            dbc.Row(dbc.Col(html.Div(style={"height": "20px"}))),
            dbc.Row([dbc.Col(tabs, width=3), dbc.Col(dbc.Button("Clear", id="btn-clear-text"), width='auto')],
                    justify="between"),
            dbc.Row(dbc.Col(html.Div(id="content"))),
        ],
        fluid=True
    )


app.layout = serve_layout

if __name__ == "__main__":
    app.run_server(debug=True)
