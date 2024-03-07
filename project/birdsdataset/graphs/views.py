# Create your views here.
from django.shortcuts import render
from plotly.offline import plot
import plotly.express as px
from birdsdataset import utils

# Create your views here.
from django.http import HttpRequest, HttpResponse


def index(request):
    context = {
        "plot" : None
    }

    #Creat the query to select the first 5 records in the table
    SQL_QUERY = """
    SELECT bird_id,
    bird_genus, bird_latitude,bird_longitute
    FROM
    [dbo].[new_birdsong];
    """
    cur = utils.connectDB()
    cursor = cur.cursor()
    cursor.execute(SQL_QUERY)

    records = cursor.fetchall()

    fig = px.scatter_mapbox(records, lat='bird_latitude', lon='bird_longitute', color='bird_genus',
                    color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10,
                    mapbox_style="carto-positron")
    
    context["plot"] = fig.to_html(full_html=False, default_height=600, default_width=800)
    
    return render(request, 'index.html', context)