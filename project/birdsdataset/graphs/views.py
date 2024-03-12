# Create your views here.
from django.shortcuts import render
from plotly.offline import plot
import plotly.express as px
from birdsdataset import utils
import pandas as pd 

# Create your views here.
from django.http import HttpRequest, HttpResponse

#Creat the query to select the first 5 records in the table
SQL_QUERY = """ SELECT * FROM [dbo].[new_birdsong];"""
cur = utils.connectDB()
cursor = cur.cursor()
cursor.execute(SQL_QUERY)

records = cursor.fetchall()
df=pd.DataFrame(records)
columns_name=df.columns

def index(request):
    context = {
        "plot" : None
    }


    if request.method == 'POST':
        # Check which button was clicked
        if 'mapButton' in request.POST:
            # Generate map plot
            print("map")
            map_fig = generate_map_plot(df)
            context["plot"] = map_fig.to_html(full_html=False, default_height=600, default_width=800)
        elif 'barButton' in request.POST:
            # Generate bar plot
            print("bar")
            bar_fig = generate_bar_plot(df)
            context["plot"] = bar_fig.to_html(full_html=False, default_height=600, default_width=800)
        elif 'pieButton' in request.POST:
            # Generate pie plot
            print("pie")
            map_fig = generate_pie_plot(df)
            context["plot"] = map_fig.to_html(full_html=False, default_height=600, default_width=800)
        elif 'lineButton' in request.POST:
            # Generate line plot
            print("line")
            map_fig = generate_line_plot(df)
            context["plot"] = map_fig.to_html(full_html=False, default_height=600, default_width=800)

    return render(request, 'index.html', context)
    
  

def generate_map_plot(df):
    fig = px.scatter_mapbox(df, lat='bird_latitude', lon='bird_longitute', color='bird_genus',
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10,
                            mapbox_style="carto-positron")
    return fig

def generate_bar_plot(df):
    df['bird_fecha'] = pd.to_datetime(df['bird_fecha'])
    agrupado = df.groupby(['bird_genus', pd.Grouper(key='bird_fecha', freq='Y')]).size().reset_index(name='count')
    #top_agrupado = agrupado.loc[(agrupado['bird_genus'] == 'Acrocephalus') | (agrupado['bird_genus'] == 'Columba') | (agrupado['bird_genus'] =='Corvus') | (agrupado['bird_genus'] =='Emberiza')|(agrupado['bird_genus'] =='Anthus')]
    #top_agrupado['bird_fecha'] = top_agrupado['bird_fecha'].dt.year
    fig = px.bar(agrupado, x="bird_genus", y="count", color="bird_fecha",
             labels={"bird_genus": "Género de pájaro", "count": "Cantidad", "bird_fecha": "Año"})
    return fig

def generate_pie_plot(df):
    pie=df.groupby(['bird_country']).count()
    pie['country']=pie.index
    fig = px.pie(pie, values='bird_id', names='country', title='contry')
    return fig
def generate_line_plot(df):
    agrupado_contry = df.groupby(['bird_country',pd.Grouper(key='bird_fecha')]).size().reset_index(name='count')
    top_contry = agrupado_contry.loc[(agrupado_contry['bird_country'] == 'United Kindom') | (agrupado_contry['bird_country'] == 'Sweden') | (agrupado_contry['bird_country'] =='Germany') | (agrupado_contry['bird_country'] =='Poland')|(agrupado_contry['bird_country'] =='Netherlands')]
    top_contry['bird_fecha'] = pd.to_datetime(agrupado_contry['bird_fecha'])
    fig = px.line(top_contry, x="bird_fecha", y="count", color="bird_country", markers=True, line_group="bird_country", hover_name="bird_country",
   render_mode="markers")
    return fig