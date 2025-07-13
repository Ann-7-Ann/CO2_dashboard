
from shiny.express import input,ui
import pandas as pd
from shinywidgets import render_plotly
import plotly.express as px


url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
data = pd.read_csv(url)
data = data[["country", "iso_code", "year", "co2"]]
data["co2"]=pd.to_numeric(data["co2"],errors="coerce")
data = data.dropna(subset= ["iso_code","co2"])
data = data[(data["iso_code"].str.len()==3) & data["co2"]>0]
countries_list = sorted(data["country"].unique())


ui.h1("CO2 dashboard")
with ui.navset_bar(title="Select your Analysis", id="selected_navset_bar"):
    with ui.nav_panel("Country - Co2 Time Series"):
        with ui.layout_sidebar():
            with ui.sidebar(

                id = "sidebar1",
                position="left",
                open= "open",):
                                
                ui.input_select(
                    id = "country",
                    label= "Choose a country",
                    choices= countries_list,
                    selected= "Austria"
                ),
                ui.input_slider(
                    id= "rolling_mean",
                    label="Rolling mean (years)",
                    min= 1,
                    max = 20,
                    value = 5
                ),
            @render_plotly
            def country_emission():
                df = data.query(f"country=='{input.country()}'")
                window = input.rolling_mean()
                df['rolling_co2'] = df['co2'].rolling(window, min_periods=1).mean()
                fig = px.line(df, x= "year", y= "co2", labels= {"co2": "CO2 [million t]", "year":"Year"},title = f"CO2 emissions - {input.country()}") 
                fig.add_scatter(x=df['year'], y=df['rolling_co2'], name = f"{input.rolling_mean()}-year-mean")
                fig.update_layout(hovermode="x unified", legend = dict(title = "Legend"))
                return fig

    with ui.nav_panel("World Map - CO2 Emissions per Country"):
        with ui.layout_sidebar():
            with ui.sidebar(

                id = "sidebar2",
                position="left",
                open= "open",):

                ui.input_slider(
                    id= "year",
                    label="Year",
                    min = data["year"].min(),
                    max = data["year"].max(),
                    value = 2007,
                    sep = "",
                ),  
            @render_plotly
            def emission_map():
                df = data.query(f"year=={input.year()}")
                fig = px.choropleth(df, 
                                    locations="iso_code",
                                    color="co2",
                                    color_continuous_scale="Reds", 
                                    labels= {"co2": "CO2 [million t]"},
                                    title=f"CO2 emissions worldwide {input.year()}",
                                    hover_name='country',
                                    hover_data=['iso_code','co2']
                          )
                fig.update_layout(margin = dict(t=40, l=0, r=0, b=0))
                return fig
                    
