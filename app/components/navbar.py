from dash import dcc, html


def create_navbar():
    return html.Div(
        className="navbar",
        children=[
            html.Div("Plateforme de scouting football", className="navbar-title"),
            html.Div(
                className="navbar-links",
                children=[
                    dcc.Link("Accueil", href="/", className="nav-link"),
                    dcc.Link("Méthodologie", href="/methodology", className="nav-link"),
                    dcc.Link("Cas d'usage", href="/use-cases", className="nav-link"),
                    dcc.Link("Validation", href="/validation", className="nav-link"),
                    dcc.Link("Scouting Lab", href="/scouting-lab", className="nav-link"),
                    dcc.Link("Shortlist", href="/shortlist", className="nav-link"),
                    dcc.Link("Explorateur joueurs", href="/player-explorer", className="nav-link"),
                    dcc.Link("Profil joueur", href="/player-profile", className="nav-link"),
                    dcc.Link("Rapport joueur", href="/player-report", className="nav-link"),
                    dcc.Link("Radar scouting", href="/scouting-radar", className="nav-link"),
                    dcc.Link("Analyse scatter", href="/scatter", className="nav-link"),
                ],
            ),
        ],
    )
