import plotly.io as pio
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc


stylesheet = [dbc.themes.BOOTSTRAP, "https://raw.githubusercontent.com/tcbegley/dash-bootstrap-css/main/dist/bootstrap/bootstrap.css"]

nacional = pd.read_csv("https://raw.githubusercontent.com/GUIAD-COVID/datos-y-visualizaciones-GUIAD/master/datos/estadisticasUY.csv",
                       index_col=0, parse_dates=True, dayfirst=True)
vacunas = pd.read_csv("https://catalogodatos.gub.uy/dataset/e766fbf7-0cc5-4b9a-a093-b56e91e88133/resource/5c549ba0-126b-45e0-b43f-b0eea72cf2cf/download/actos_vacunales.csv",
                      sep=";", index_col=0, parse_dates=True, dayfirst=True).sort_index()
cti = pd.read_csv("https://raw.githubusercontent.com/GUIAD-COVID/datos-y-visualizaciones-GUIAD/master/datos/estadisticasUY_cti.csv",
                  index_col="fecha", parse_dates=True, dayfirst=True).sort_index()
cti["ocupacion_nocovid"] = cti["ocupacion_total"] - cti["ocupacion_covid"]

latest_nat = nacional.iloc[-1][["cantCasosNuevosConsolidado", "cantRecuperados", "cantFallecidos", "cantCTI", "cantTest"]]
latest_vac = vacunas.iloc[-1][["Total Dosis 1", "Total Dosis 2"]].sum()
latest_nat["Positividad"] = round(latest_nat["cantCasosNuevosConsolidado"] / latest_nat["cantTest"] * 100, 1)
latest = latest_nat
latest["Vacunación"] = latest_vac
latest.index = ["Casos nuevos", "Recuperados", "Fallecidos", "CTI", "Tests", "Positividad", "Vacunados"]
latest = latest.to_frame().T

pio.templates.default = "plotly_white"

app = Dash(__name__, external_stylesheets=stylesheet,
                  meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}])

def update_fig_layout(fig):
    fig.update_layout(legend=dict(yanchor="top", y=-0.1,
                                  xanchor="left", x=0.0,
                                  title_text="",
                                  orientation="h"),
                      showlegend=True,
                      xaxis={"title_text": ""},
                      yaxis={"title_text": ""},
                      font_family="Helvetica",
                      font_color="#8C8C8C",
                      margin={"r":0,"t":60,"l":0,"b":40})
    return

tab_1 = [html.Br(),
         dbc.Row([
             dbc.Col(dcc.Graph(id="chart-casos-nuevos"), md=6),
             dbc.Col(dcc.Graph(id="chart-casos-acum"), md=6),
], className="g-0")]


tab_2 = [html.Br(),
         dbc.Row([
             dbc.Col(dcc.Graph(id="chart-fallecidos"), md=6),
             dbc.Col(dcc.Graph(id="chart-fallecidos-acum"), md=6),
], className="g-0")]

tab_3 = [html.Br(),
         dbc.Row([
             dbc.Col(dcc.Graph(id="chart-tests"), md=6),
             dbc.Col(dcc.Graph(id="chart-positividad"), md=6),
], className="g-0")]


tab_4 = [html.Br(),
         dbc.Row([
             dbc.Col(dcc.Graph(id="chart-cti"), md=6),
             dbc.Col(dcc.Graph(id="chart-cti-camas"), md=6),
], className="g-0"),
        dbc.Row([
             dbc.Col(dcc.Graph(id="chart-cti-ocupacion"), md=6),
             dbc.Col(dcc.Graph(id="chart-cti-flujos"), md=6),
], className="g-0")]


app.layout = dbc.Container([html.H1("Monitor COVID-19 en Uruguay"),
                            html.Div(f"Actualización: {latest.index[0].strftime('%d-%m-%y')}"),
                            html.Br(),
                            dbc.Card([dbc.CardHeader(html.H5("Últimos datos")),
                                      dbc.CardBody(
                                          dbc.Table.from_dataframe(latest, striped=True, hover=True,
                                                                   bordered=True, responsive=True, className="table-sm"))],
                                     color="primary", outline=True),
                            html.Br(),
                            dbc.Row([
                                dbc.Col(
                                    dbc.Select(id="rolling-select",
                                               options=[{"label": "No agregar promedio", "value": "0"},
                                                        {"label": "7 días", "value": "P7"},
                                                        {"label": "14 días", "value": "P14"}],
                                               placeholder="Agregar promedio"), md=6),
                                dbc.Col(
                                    html.Div(dcc.DatePickerRange(id="dates", display_format="DD-MM-YY",
                                                        start_date_placeholder_text="Fecha inicio",
                                                        end_date_placeholder_text="Fecha fin",
                                                        min_date_allowed="2020-03-25",
                                                        start_date="2020-03-25"), className="dash-bootstrap"), md=6)]),
                            html.Br(),
                            dbc.Tabs([dbc.Tab(tab_1, label="Casos"),
                                      dbc.Tab(tab_2, label="Fallecimientos"),
                                      dbc.Tab(tab_3, label="Tests"),
                                      dbc.Tab(tab_4, label="CTI")])],
                           fluid=True)

@app.callback(
[Output("chart-casos-nuevos", "figure"),
 Output("chart-fallecidos", "figure"),
 Output("chart-tests", "figure"),
 Output("chart-positividad", "figure")],
[Input("rolling-select", "value"),
 Input("dates", "start_date"),
 Input("dates", "end_date")])
def crear_graficos_flujos(promedio, start, end, data=nacional):
    start = start or "2020-03-25"
    end = end or dt.date.today().strftime("%Y-%m-%d")
    data = data.loc[start:end]
    figs = []
    if not promedio or promedio == "0":
        for col, title in zip(["cantCasosNuevosConsolidado", "cantFallecidos", "cantTest", "Positividad"],
                              ["Casos nuevos", "Fallecimientos", "Tests realizados", "Positividad"]):
            figs.append(px.line(data_frame=data, y=col, title=title, color_discrete_sequence=px.colors.qualitative.Vivid))
    else:
        for col, title in zip(["cantCasosNuevosConsolidado", "cantFallecidos", "cantTest", "Positividad"],
                              ["Casos nuevos", "Fallecimientos", "Tests realizados", "Positividad"]):
            data[f"{col} - P7"] = data[col].rolling(7).mean()
            data[f"{col} - P14"] = data[col].rolling(14).mean()
            figs.append(px.line(data_frame=data, y=[col] + [f"{col} - {promedio}"],
                                title=title, color_discrete_sequence=px.colors.qualitative.Vivid))
    for fig in figs:
        update_fig_layout(fig)
    return figs

@app.callback(
[Output("chart-casos-acum", "figure"),
 Output("chart-fallecidos-acum", "figure"),
 Output("chart-cti", "figure"),
 Output("chart-cti-camas", "figure"),
 Output("chart-cti-ocupacion", "figure"),
 Output("chart-cti-flujos", "figure")],
[Input("dates", "start_date"),
 Input("dates", "end_date")])
def crear_graficos_resto(start, end, nacional=nacional, cti=cti):
    start = start or "2020-03-25"
    end = end or dt.date.today().strftime("%Y-%m-%d")
    nacional = nacional.loc[start:end, :]
    cti = cti.loc[start:end, :]
    fig_casos_acum = px.area(data_frame=nacional, y="acumCasos",
                             title="Casos acumulados", color_discrete_sequence=px.colors.qualitative.Vivid)
    fig_fallecidos_acum = px.area(data_frame=nacional, y="acumFallecidos", title="Fallecimientos acumulados",
                                  color_discrete_sequence=px.colors.qualitative.Vivid)
    fig_cti = px.bar(data_frame=cti, y="cant_pacientes", title="Pacientes en CTI",
                      color_discrete_sequence=px.colors.qualitative.Vivid)
    fig_cti_camas = px.line(data_frame=cti, y=["camas_operativas", "camas_ocupadas"], title="Camas de CTI",
                      color_discrete_sequence=px.colors.qualitative.Vivid)
    fig_cti_ocupacion = px.area(data_frame=cti, y=["ocupacion_nocovid", "ocupacion_covid"], title="Camas de CTI",
                      color_discrete_sequence=px.colors.qualitative.Vivid)
    fig_cti_flujos = px.line(data_frame=cti, y=["ingresos", "fallecimientos", "altas_medicas"], title="Flujo de personas en CTI",
                            color_discrete_sequence=px.colors.qualitative.Vivid)
    figs = [fig_casos_acum, fig_fallecidos_acum, fig_cti, fig_cti_camas, fig_cti_ocupacion, fig_cti_flujos]
    for fig in figs:
        update_fig_layout(fig)
    return figs


if __name__ == '__main__':
    app.run_server()
