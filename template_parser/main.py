import logging.config
from textwrap import dedent

import dash_bootstrap_components as dbc
from dash import html, Dash, Input, Output, dcc, State, ALL
from dash.exceptions import PreventUpdate

from template_parser.process_textfsm import parse_textfsm
from template_parser.process_ttp import parse_ttp

logging.disable()
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
app.title = "Template Parser"

TEMPLATE_LANGUAGES = {
    "ttp": {"name": "TTP"},
    "textfsm": {"name": "TextFSM"},
}


def add_clipboard(target_id):
    return dcc.Clipboard(
        target_id=target_id,
        title="copy",
        style={
            "position": "absolute",
            "top": 30,
            "right": 10,
            "fontSize": 20,
        },
    )


def add_editor(textarea_id: dict, placeholder_text: str):
    return dbc.Textarea(
        id=textarea_id,
        placeholder=placeholder_text,
        style={"height": "100%", "resize": "None"},
        persistence=True,
        persistence_type="session",
        spellcheck=False,
        className="mb-3",
    )


def build_page_content(template_language: str):
    if template_language not in TEMPLATE_LANGUAGES:
        return html.Div("404")
    data = TEMPLATE_LANGUAGES[template_language]
    language_name = data.get("name", template_language)

    return dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        add_editor(
                            {"type": "raw-input", "index": template_language},
                            "Enter raw text",
                        ),
                        add_clipboard(
                            {"type": "raw-input", "index": template_language}
                        ),
                    ],
                    style={"position": "relative", "height": "100%"},
                )
            ),
            dbc.Col(
                html.Div(
                    [
                        add_editor(
                            {"type": "input", "index": template_language},
                            f"Enter {language_name} template",
                        ),
                        add_clipboard({"type": "input", "index": template_language}),
                    ],
                    style={"position": "relative", "height": "100%"},
                )
            ),
            dbc.Col(
                dbc.Card(
                    [
                        html.Div(
                            dcc.Markdown(
                                children="Results will appear here",
                                id={"type": "output", "index": template_language},
                                style={
                                    "resize": "None",
                                    "white-space": "pre",
                                },
                            ),
                            style={
                                "padding": "10px",
                                "overflow": "auto",
                            },
                        ),
                        add_clipboard({"type": "output", "index": template_language}),
                    ],
                    style={"position": "relative", "height": "100%"},
                ),
                style={"max-height": "100%"},
            ),
        ],
        style={"height": "90vh"},
    )


tabs = html.Div(
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
    except (Exception, SystemExit):
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
        result = dedent(
            f"""\
```
{result}
```
"""
        )
        return result, False
    except RuntimeError:
        return existing_result, True


@app.callback(
    Output({"type": "input", "index": ALL}, "value", allow_duplicate=True),
    Output({"type": "raw-input", "index": ALL}, "value", allow_duplicate=True),
    Output({"type": "output", "index": ALL}, "children", allow_duplicate=True),
    Input("btn-clear-text", "n_clicks"),
    prevent_initial_call=True,
)
def clear_templates(_):
    return [""], [""], ["Results will appear here"]


def serve_layout():
    return dbc.Container(
        [
            dbc.Row(dbc.Col(html.Div(style={"height": "20px"}))),
            dbc.Row(
                [
                    dbc.Col(tabs, width=3),
                    dbc.Col(dbc.Button("Clear", id="btn-clear-text"), width="auto"),
                ],
                justify="between",
            ),
            dbc.Row(dbc.Col(html.Div(id="content"))),
        ],
        fluid=True,
    )


app.layout = serve_layout

if __name__ == "__main__":
    app.run_server(debug=True)
