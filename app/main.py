# app/app.py

from dash import Dash, dcc, html
import dash

from app.components.navbar import create_navbar


app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
app.title = "Plateforme de scouting football"

server = app.server


app.layout = html.Div(
    children=[
        dcc.Location(id="url"),
        create_navbar(),
        html.Div(dash.page_container, className="main-container"),
    ]
)


if __name__ == "__main__":
    app.run(debug=True)
