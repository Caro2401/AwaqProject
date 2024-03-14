# Create your views here.
from django.shortcuts import render
from plotly.offline import plot
import plotly.express as px
from birdsdataset import utils
import pandas as pd 
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import io

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
        dtype = request.POST.get('dtype')
        # Check which button was clicked
        if dtype=='mapButton':
            # Generate map plot
            print("map")
            map_fig = generate_map_plot(df)
            context["plot"] = map_fig.to_html(full_html=False, default_height=600, default_width=800)

        elif dtype=='bar_genus':
            # Generate bar plot
            print("bar")
            bar_fig = generate_bar_plot(df,False,False)
            context["plot"] = bar_fig.to_html(full_html=False, default_height=600, default_width=800)

        elif dtype=='bar_topgenus':
            # Generate pie plot
            print("bar_top")
            bar_fig = generate_bar_plot(df,True,False)
            context["plot"] = bar_fig.to_html(full_html=False, default_height=600, default_width=800)

        elif  dtype=='bar_buttomgenus':
            # Generate line plot
            print("bar_buttom")
            bar_fig = generate_bar_plot(df,False,True)
            context["plot"] = bar_fig.to_html(full_html=False, default_height=600, default_width=800)

        elif  dtype=='pie_country':
            # Generate line plot
            print("pie_country")
            pie_fig = generate_pie_plot(df,"bird_country")
            context["plot"] = pie_fig.to_html(full_html=False, default_height=600, default_width=800)

        elif  dtype=='pie_song':
            
            print("pie_song")
            pie_fig = generate_pie_plot(df,"bird_type1")
            context["plot"] = pie_fig.to_html(full_html=False, default_height=600, default_width=800)

        elif  dtype=='word_reg':
            # Generate line plot
            print("word")
            word_fig = generate_word_plot(df)
            context["plot"] = word_fig

        elif  dtype=='line_reg':
            # Generate line plot
            print("line")
            line_fig = generate_line_plot(df,False)
            context["plot"] = line_fig.to_html(full_html=False, default_height=600, default_width=1000)

        elif  dtype=='line_topreg':
            # Generate line plot
            print("line")
            line_fig = generate_line_plot(df,True)
            context["plot"] = line_fig.to_html(full_html=False, default_height=600, default_width=800)


    return render(request, 'index.html', context)
    
  

def generate_map_plot(df):
    fig = px.scatter_mapbox(records, lat='bird_latitude', lon='bird_longitute', color='bird_genus',
                  color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=1,
                  mapbox_style="carto-positron")
    fig.update_layout(
    title="Mapa de registros por genero ",

)
    return fig

def generate_bar_plot(df,top,buttom):
    df['bird_fecha'] = pd.to_datetime(df['bird_fecha'])
    agrupado = df.groupby(['bird_genus', pd.Grouper(key='bird_fecha', freq='Y')]).size().reset_index(name='count')
    agrupado=agrupado.sort_values(by='count', ascending=False)
    if top==True:
        agrupado= agrupado.head(5)
        agrupado['bird_fecha'] = agrupado['bird_fecha'].dt.year
        agrupado['text'] = agrupado['bird_fecha'].astype(str) + '<br>' + 'registros: ' + agrupado['count'].astype(str)

        fig = px.bar(agrupado, x="count", y="bird_genus",  text="text",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    labels={'bird_genus': 'Género de Ave', 'count': 'Cantidad'})
        fig.update_layout(title="Registros por especie de las especies con mas registros",yaxis={'categoryorder':'total ascending'}) 
        fig.update_traces(texttemplate='%{text}', textposition='inside') # Opcional: Ordenar las barras horizontalmente
    elif buttom==True:
        agrupado= agrupado.tail(5)
        agrupado['bird_fecha'] = agrupado['bird_fecha'].dt.year
        agrupado['text'] = agrupado['bird_fecha'].astype(str) + '<br>' + 'registros: ' + agrupado['count'].astype(str)

        fig = px.bar(agrupado, x="count", y="bird_genus",  text="text",
                    labels={'bird_genus': 'Género de Ave', 'count': 'Cantidad'})
        fig.update_layout(title="Registros por especie de las especies con menores registros",yaxis={'categoryorder':'total ascending'}) 
        fig.update_traces(texttemplate='%{text}', textposition='inside') # Opcional: Ordenar las barras horizontalmente
    else:
        fig = px.bar(agrupado , x='bird_genus', y='count', text='bird_fecha')
        fig.update_layout(
            title="Registros por especie",
            xaxis_title="Especie",
            yaxis_title="Numero de registros",
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1
        )

    return fig

def generate_pie_plot(df,data):
    pie=df.groupby([data]).size().reset_index(name='count')
    fig = px.pie(pie, values='count', names=data, title='Porcentaje de registros por:'+data)
    return fig

def generate_word_plot(df):
    word = df.groupby(['bird_provided_recording']).size().reset_index(name='count')
    text = ' '.join([letra * count for letra, count in zip(word['bird_provided_recording'], word['count'])])

    # Crear el WordCloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Configurar el tamaño de la figura
    plt.figure(figsize=(10, 5))
    
    # Mostrar el WordCloud en la figura
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic_str = base64.b64encode(image_png).decode('utf-8')
    html_str = f'<img src="data:image/png;base64,{graphic_str}">'
    
    return html_str
 


def generate_line_plot(df,top):

    if top==False:
        agrupado = df.groupby(['bird_fecha']).size().reset_index(name='count')
        agrupado['bird_fecha'] = agrupado['bird_fecha'].astype(str)
        top_cinco = agrupado.sort_values(by='count', ascending=False)
        top_cinco = top_cinco.head(5)
        fig = px.line(agrupado, x='bird_fecha', y="count",markers=True, 
        render_mode="markers")
        fig.add_trace(px.scatter(top_cinco, x='bird_fecha', y="count", text='count').data[0])
        fig.update_traces(textposition='top center')
        fig.update_layout(
            title="Registros por fecha ",
            xaxis_title="Fecha",
            yaxis_title="Numero de registros"
        )

    elif top==True:
        agrupado_contry = df.groupby(['bird_country',pd.Grouper(key='bird_fecha')]).size().reset_index(name='count')
        top_contry = agrupado_contry.loc[(agrupado_contry['bird_country'] == 'United Kindom') | (agrupado_contry['bird_country'] == 'Sweden') | (agrupado_contry['bird_country'] =='Germany') | (agrupado_contry['bird_country'] =='Poland')|(agrupado_contry['bird_country'] =='Netherlands')]
        top_contry['bird_fecha'] = pd.to_datetime(agrupado_contry['bird_fecha'])
        fig = px.line(top_contry, x="bird_fecha", y="count", color="bird_country", markers=True, line_group="bird_country", hover_name="bird_country",
    render_mode="markers")
        fig.update_layout(
            title="Registros por fecha de los paises con más registros ",
            xaxis_title="Fecha",
            yaxis_title="Numero de registros"
        )
    return fig