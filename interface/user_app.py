import dash
import dash_bootstrap_components as dbc


app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY])

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(page["name"], href=page["path"], style={'font-size': '20px'})) 
        for page in dash.page_registry.values() if page["module"] != "pages.not_found_404"
    ],
    brand="WatchPlant Dashboard",
    brand_style={"font-size": "40px"},  # Increase the font size of the brand
    color="primary",
    dark=True,
    className="mb-2",
)

app.layout = dbc.Container(
    [navbar, dash.page_container],
    fluid=True,
)

# Run the app
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=False)
    # app.run_server(host='0.0.0.0', port=8050)