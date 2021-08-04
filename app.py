# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
from pitch import Pitch
from PIL import Image

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{
        'name': 'viewport',
        'content': 'width=device-width, initial-scale=1.0'
    }]
)

clubs = pd.read_csv("data/clubs_extended.csv")
players = pd.read_csv("data/players_extended.csv")
games = pd.read_csv("data/games_extended.csv")

def who_won(home_club_goals, away_club_goals):
    """

    """
    if home_club_goals > away_club_goals:
        return "home"
    elif away_club_goals > home_club_goals:
        return "away"
    else:
        return "draw"

def get_higher_market_value(home_team, away_team):
    if home_team > away_team:
        return "home"
    elif away_team > home_team:
        return "away"
    else:
        return "draw"

def calculate_advantage_results(games_):
    advantage_results_league = {"win": 0, "draw": 0, "loss": 0}

    for _, row in games_.iterrows():
        home_club_goals = row["home_club_goals"]
        away_club_goals = row["away_club_goals"]
        result = who_won(home_club_goals, away_club_goals)
        
        weighted_market_value_home = row["weighted_market_value_home"]
        weighted_market_value_away = row["weighted_market_value_away"]
        market_value_advantage = get_higher_market_value(weighted_market_value_home, weighted_market_value_away)
        
        if result == market_value_advantage:
            advantage_results_league["win"] += 1
        else:
            if result == "draw":
                advantage_results_league["draw"] += 1
            else:
                advantage_results_league["loss"] += 1

    advantage_results_df = pd.DataFrame.from_dict(advantage_results_league, orient='index', columns=["results"])
    fig = px.pie(advantage_results_df, values="results", names=advantage_results_df.index)
    return fig

navbar = dbc.Row(
    [
        dbc.Col(html.Img(src="assets/tm-logo.png", height="50px"), width=2),
        dbc.Col(dbc.NavbarBrand("Sports Analytics: Transfermarkt Data Visualization"), className="text-center", width=8),
        dbc.Col(html.Img(src="assets/liu-logo.png", height="50px", className="float-right"), width=2)
    ],
    align="center",
    no_gutters=True,
    justify="between",
    style={"padding": "10px"}
)

def density_map(clubs):
    return (
        dbc.Card(
            dbc.CardBody(
                [
                    html.H4("Geographical Market Value Distribution - Top 5 Leagues", className="card-title"),
                    dcc.Graph(figure=px.density_mapbox(
                        clubs, 
                        lat='latitude', 
                        lon='longitude', 
                        z='market_value', 
                        radius=15, 
                        hover_name='pretty_name',
                        labels={'market_value': 'Market Value'},
                        center=dict(lat=47.6667, lon=3.6667), 
                        zoom=2,
                        mapbox_style="stamen-toner")),
                ]
            ),
        )
    )


def density_pitch():
    return (dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4("Positional Market Value Distribution", className="card-title"),
                        dcc.Dropdown(
                            id='density-pitch-dropdown',
                            options=[
                                {'label': 'Sum', 'value': 'SUM'},
                                {'label': 'Mean', 'value': 'MEAN'},
                                {'label': 'Maximum', 'value': 'MAX'}
                            ],
                            value='SUM'                        ),
                        dcc.Graph(
                            id="density-pitch",
                            figure={}
                        )
                    ]
                )
            ]
        )
    )

def base_club_stats():
    return (dbc.Row(id="base-club-stats", style={"marginBottom": "20px"}))

def base_player_stats():
    return (dbc.Row(id="base-player-stats", style={"marginBottom": "20px"}))

def players_table():
    data_columns = ["Name", "Age", "Club", "Position", "Games", "Minutes played", "Goals", "Assists", "Wins", "Draws", "Losses", "Market Value"]
    df_columns = ["pretty_name", "age", "club_name", "sub_position", "games", "minutes_played", "goals", "assists", "wins", "draws", "losses", "market_value"]
        
    return (dbc.Card
        ([
            dbc.CardBody(
                [
                    html.H4("Player Details - Season 2020/2021", className="card-title"),
                    dash_table.DataTable(
                        id="players-table",
                        columns=[{
                            'name': col, 
                            'id': df_columns[idx]
                        } for (idx, col) in enumerate(data_columns)],
                        style_table={'overflowX': 'auto'},
                        page_size=10)            
                ]
            )
        ])
    )

def bar_chart():      
    return (dbc.Card
        ([
            dbc.CardBody(
                [
                    html.H4("Market Value by Position and Club", className="card-title"),
                    dcc.Graph(
                        id="bar-chart",
                        figure={}
                    )           
                ]
            )
        ])
    )

def pie_chart():
    return (
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4("Did the Team with higher Market Value win?", className="card-title"),
                                    html.P(
                                        [   
                                            {}
                                        ],
                                        id="pie-chart-leaguename",
                                        className="card-text"
                                    ),
                                    dcc.Graph(
                                        id="pie-chart-league",
                                        figure={}
                                    )         
                                ]
                            )
                        ]
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4("Did the Team with higher Market Value win?", className="card-title"),
                                    html.P(
                                        [   
                                            {}
                                        ],
                                        id="pie-chart-clubname",
                                        className="card-text"
                                    ),
                                    dcc.Graph(
                                        id="pie-chart-team",
                                        figure={}
                                    )           
                                ]
                            )
                        ]
                    )
                )
            ],
            style={"marginBottom": "20px"}
        )
    )

app.layout = dbc.Container([
    navbar,
    dbc.Row(
        [
            dbc.Col(dcc.Dropdown(
                id='league-dropdown',
                multi=True,
                options=[
                    {'label': 'Premier League', 'value': 'GB1'},
                    {'label': 'Bundesliga', 'value': 'L1'},
                    {'label': 'La Liga', 'value': 'ES1'},
                    {'label': 'Serie A', 'value': 'IT1'},
                    {'label': 'Ligue 1', 'value': 'FR1'}
                ],
                value=['GB1']
            ))
        ],
        style={"marginBottom": "20px"}
    ),
    base_club_stats(),
    base_player_stats(),
    dbc.Row(
        [
            dbc.Col(bar_chart())
        ],
        style={"marginBottom": "20px"}
    ),
    dbc.Row(
        [
            dbc.Col(density_pitch())
        ],
        style={"marginBottom": "20px"}
    ),
    dbc.Row(
        [
            dbc.Col(players_table())
        ],
        style={"marginBottom": "20px"}
    ),
    dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(
                    id='pie-chart-league-dropdown',
                    options=[
                        {'label': 'Premier League', 'value': 'GB1'},
                        {'label': 'Bundesliga', 'value': 'L1'},
                        {'label': 'La Liga', 'value': 'ES1'},
                        {'label': 'Serie A', 'value': 'IT1'},
                        {'label': 'Ligue 1', 'value': 'FR1'}
                    ],
                    value='GB1'
                )
            ),
            dbc.Col(
                dcc.Dropdown(
                    id='pie-chart-team-dropdown',
                    value='Manchester United'
                )
            )
        ],
        style={"marginBottom": "20px"}
    ),
    pie_chart(),
    dbc.Row(
        [
            dbc.Col(density_map(clubs))
        ],
        style={"marginBottom": "20px"}
    )
])

@app.callback(
    [
        Output('bar-chart', 'figure'),
        Output('players-table', 'data'),
        Output('base-club-stats', 'children'),
        Output('base-player-stats', 'children'),
        Output('density-pitch', 'figure')
    ], 
    [
        Input('league-dropdown', 'value'),
        Input('density-pitch-dropdown', 'value')
    ])
def update_dashboard(league_ids, filter):
    if len(league_ids) > 0:
        print(f"Values chosen: {league_ids}")

        players_ = players[players["league_id"].isin(league_ids)]
        clubs_ = clubs[clubs["league_id"].isin(league_ids)]

        #################
        ### bar-chart ###
        #################
        grouped_df = players_.groupby(["club_name", "position"])["market_value"].sum().reset_index()
        fig = px.bar(grouped_df, x="club_name", y="market_value", color="position", labels={
                     "club_name": "Club",
                     "market_value": "Market Value (€)",
                     "position": "Positions"
                 })
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        #####################
        ### players-table ###
        #####################
        players_ = players_[["pretty_name", "age", "club_name", "sub_position", "games", "minutes_played", "goals", "assists", "wins", "draws", "losses", "market_value"]].sort_values("market_value", ascending=False)
        players_table = players_.to_dict('records')

        #######################
        ### base-club-stats ###
        #######################
        highest_club_value = dict(clubs_.loc[clubs_['market_value'].idxmax()])
        lowest_club_value = dict(clubs_.loc[clubs_['market_value'].idxmin()])
        mean_club_value = int(clubs_['market_value'].mean())
        median_club_value = int(clubs_['market_value'].median())

        base_club_stats = [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4("{:,}€".format(highest_club_value['market_value']), className="card-title"),
                                html.P(
                                    [   
                                        "Highest Club Value",
                                        html.Br(),
                                        highest_club_value['pretty_name']
                                    ],
                                    className="card-text"
                                )            
                            ]
                        )
                    ]
                )
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4("{:,}€".format(lowest_club_value['market_value']), className="card-title"),
                                html.P(
                                    [   
                                        "Lowest Club Value",
                                        html.Br(),
                                        lowest_club_value['pretty_name']
                                    ],
                                    className="card-text"
                                )            
                            ]
                        )
                    ]
                )
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4("{:,}€".format(mean_club_value), className="card-title"),
                                html.P(
                                    [
                                        "Mean Club Value",
                                        html.Br(), 
                                        html.Br()
                                    ], 
                                    className="card-text")            
                            ]
                        )
                    ]
                )
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4("{:,}€".format(median_club_value), className="card-title"),
                                html.P(
                                    [
                                        "Median Club Value",
                                        html.Br(), 
                                        html.Br()
                                    ], 
                                    className="card-text"
                                )            
                            ]
                        )
                    ]
                )
            )
        ]

        #########################
        ### base-player-stats ###
        #########################
        highest_player_value = dict(players_.loc[players_['market_value'].idxmax()])
        lowest_player_value = dict(players_.loc[players_['market_value'].idxmin()])
        mean_player_value = int(players_['market_value'].mean())
        median_player_value = int(players_['market_value'].median())

        base_player_stats = [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4("{:,}€".format(highest_player_value['market_value']), className="card-title"),
                                html.P(
                                    [   
                                        "Highest Player Value",
                                        html.Br(),
                                        highest_player_value['pretty_name']
                                    ],
                                    className="card-text"
                                )            
                            ]
                        )
                    ]
                )
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4("{:,}€".format(lowest_player_value['market_value']), className="card-title"),
                                html.P(
                                    [   
                                        "Lowest Player Value",
                                        html.Br(),
                                        lowest_player_value['pretty_name']
                                    ],
                                    className="card-text"
                                )            
                            ]
                        )
                    ]
                )
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4("{:,}€".format(mean_player_value), className="card-title"),
                                html.P(
                                    [
                                        "Mean Player Value",
                                        html.Br(), 
                                        html.Br()
                                    ], 
                                    className="card-text")            
                            ]
                        )
                    ]
                )
            ),
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4("{:,}€".format(median_player_value), className="card-title"),
                                html.P(
                                    [
                                        "Median Player Value",
                                        html.Br(), 
                                        html.Br()
                                    ], 
                                    className="card-text"
                                )            
                            ]
                        )
                    ]
                )
            )
        ]

        #####################
        ### density-pitch ###
        #####################
        pitch = Pitch(players_)

        # Check filter
        if filter == "SUM":
            pitch.position_data = pitch.marketvalue_sum_by_position()
        elif filter == "MEAN":
            pitch.position_data = pitch.marketvalue_mean_by_position()
        elif filter == "MAX":
            pitch.position_data = pitch.marketvalue_max_by_position()
        else:
            pass

        pitch.position_data = pitch.convert_position_to_coordinates()

        # Insert row at index 0 containing values [0, 0, 0] for heatmap X and Y axis scaling
        pitch.position_data.loc[-1] = [0, 0, 0]
        pitch.position_data.index = pitch.position_data.index + 1 
        pitch.position_data = pitch.position_data.sort_index()

        # Append row containing values [130, 90, 0] for heatmap X and Y axis scaling
        end = pd.DataFrame([[130, 90, 0]], columns=["X", "Y", "market_value"])
        pitch.position_data = pitch.position_data.append(end, ignore_index=True)

        img = Image.open('./assets/pitch.jpg')
        density_pitch = go.Figure()

        density_pitch.add_trace(go.Contour(
                x=pitch.position_data["X"], 
                y=pitch.position_data["Y"], 
                z=pitch.position_data["market_value"],
                showscale=True, 
                connectgaps=True, 
                hoverinfo="none",
                opacity=0.5))


        # axis hide、yaxis reversed
        density_pitch.update_layout(
            autosize=False,
            width=1047,
            height=705,
            xaxis=dict(visible=False,autorange=True),
            yaxis=dict(visible=False,autorange='reversed')
        )

        # background image add
        density_pitch.add_layout_image(
            dict(source=img,
                xref='x',
                yref='y',
                x=0,
                y=0,
                sizex=130,
                sizey=90,
                sizing='stretch',
                opacity=1,
                layer='below')
        )

        return fig, players_table, base_club_stats, base_player_stats, density_pitch

@app.callback(
        Output('pie-chart-team-dropdown', 'options'), 
        Input('pie-chart-league-dropdown', 'value'))
def set_team_options(selected_league):
    all_options = {
        'GB1': ['Wolverhampton Wanderers', 'West Ham United', 'Sheffield United',
                'Fc Liverpool', 'Manchester City', 'Leicester City',
                'Leeds United', 'Aston Villa', 'Fc Arsenal', 'Fc Burnley',
                'Crystal Palace', 'Fc Fulham', 'Newcastle United', 'Fc Chelsea',
                'Fc Southampton', 'Manchester United', 'Tottenham Hotspur',
                'Fc Everton', 'Brighton Amp Hove Albion', 'West Bromwich Albion'],
        'L1': ['Vfb Stuttgart', 'Sv Werder Bremen', '1 Fc Koln',
                'Eintracht Frankfurt', 'Tsg 1899 Hoffenheim', 'Vfl Wolfsburg',
                'Borussia Dortmund', 'Fc Bayern Munchen', 'Rasenballsport Leipzig',
                'Arminia Bielefeld', 'Hertha Bsc', 'Fc Augsburg', 'Sc Freiburg',
                'Bayer 04 Leverkusen', 'Borussia Monchengladbach', 'Fc Schalke 04',
                '1 Fsv Mainz 05', '1 Fc Union Berlin'],
        'ES1': ['Fc Sevilla', 'Fc Granada', 'Real Valladolid', 'Real Madrid',
                'Sd Huesca', 'Ca Osasuna', 'Sd Eibar', 'Celta Vigo',
                'Fc Villarreal', 'Fc Valencia', 'Fc Getafe', 'Fc Cadiz',
                'Fc Barcelona', 'Atletico Madrid', 'Real Sociedad San Sebastian',
                'Real Betis Sevilla', 'Athletic Bilbao', 'Ud Levante', 'Fc Elche',
                'Deportivo Alaves'],
        'IT1': ['Ssc Neapel', 'Spezia Calcio', 'Atalanta Bergamo', 'Fc Bologna',
                'Fc Turin', 'Cagliari Calcio', 'Fc Crotone', 'Hellas Verona',
                'Ac Mailand', 'Udinese Calcio', 'Inter Mailand', 'Ac Florenz',
                'As Rom', 'Juventus Turin', 'Sampdoria Genua', 'Genua Cfc',
                'Parma Calcio 1913', 'Lazio Rom', 'Benevento Calcio',
                'Us Sassuolo'],
        'FR1': ['Fc Nantes', 'Sco Angers', 'As Saint Etienne', 'Rc Lens',
                'Fc Metz', 'Rc Strassburg Alsace', 'Stade Brest 29',
                'Olympique Lyon', 'Fc Paris Saint Germain', 'Nimes Olympique',
                'Montpellier Hsc', 'Stade Reims', 'As Monaco',
                'Olympique Marseille', 'Dijon Fco', 'Losc Lille', 'Fc Lorient',
                'Fc Girondins Bordeaux', 'Ogc Nizza', 'Fc Stade Rennes']

    }
    return [{'label': i, 'value': i} for i in all_options[selected_league]]

@app.callback(
    [
        Output('pie-chart-league', 'figure'),
        Output('pie-chart-team', 'figure'),
        Output('pie-chart-leaguename', 'children'),
        Output('pie-chart-clubname', 'children')
    ], 
    [
        Input('pie-chart-league-dropdown', 'value'),
        Input('pie-chart-team-dropdown', 'value')
    ]
)
def update_pie_charts(league, team):
    games_ = games[games['league_code'] == league]
    advantage_results_league_fig = calculate_advantage_results(games_)

    league_dict = {
        'GB1': 'Premier League',
        'L1': 'Bundesliga',
        'ES1':'La Liga',
        'IT1':'Serie A',
        'FR1':'Ligue 1'
    }
    league_name = "{} Average 2020/2021".format(league_dict[league])

    games__ = games.loc[(games['home_club_name'] == team) | (games['away_club_name'] == team)]
    advantage_results_team_fig = calculate_advantage_results(games__)

    club_name = "{} 2020/2021".format(team)
    
    return advantage_results_league_fig, advantage_results_team_fig, league_name, club_name

if __name__ == '__main__':
    app.run_server()