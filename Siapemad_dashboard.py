import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image, ImageOps
from datasets import excel_files_actividad, excel_files_consumo, image_paths
from actividad import Actividad


# Store the initial value of widgets in session state
if "login_complete" not in st.session_state:
    st.session_state.login_complete = False

user1 = st.secrets["secrets"]["USER1"]
pass1 = st.secrets["secrets"]["PASS1"]
usuarios = {
    user1: pass1
    # Agrega más usuarios si es necesario
}

# Variables Globales graficos
FONT_SIZE = 20
TITLE_SIZE = 23
XAXIS_SIZE = 18
YAXIS_SIZE = 18
LEGEND_SIZE = 17
TITLEX_SIZE = 21
TITLEY_SIZE = 21

# Configuración inicial de la página
st.set_page_config(page_title="Métricas de SIAPEMAD",
                   page_icon=":bar_chart:",
                   layout="wide")

# Inicialización del estado de la sesión
if "data_actividad" not in st.session_state:
    st.session_state.data_actividad = None
if "data_consumo" not in st.session_state:
    st.session_state.data_consumo = None


def login():
    """Función para el inicio de sesión."""
    st.title("Inicio de sesión")
    st.write("Por favor, introduce tu nombre de usuario y contraseña.")

    # Entradas de texto para usuario y contraseña
    username = st.text_input("Usuario", key="username_input")
    password = st.text_input("Contraseña", type="password", key="password_input")
    buton = st.button("Iniciar sesión", key="login_button")
    # Botón para iniciar sesión
    if buton:
        if username in usuarios:
            if usuarios[username] == password:
                st.success(f"Bienvenido, {username}!")
                # Actualizar el estado de la sesión para indicar que el inicio de sesión está completo
                st.session_state.login_complete = True
                st.experimental_rerun()  # Refrescar la página para ocultar los campos de texto
                return True
            else:
                st.error("Contraseña incorrecta. Inténtalo de nuevo.")
        else:
            st.error("Usuario no encontrado.")
    
    return False

def encabezado():
    """Muestra el encabezado y las imágenes en la página principal."""
    uniform_width = 300  # Anchura uniforme deseada

    # Calcular la altura máxima de las imágenes redimensionadas
    heights = []
    for img_path in image_paths:
        img = Image.open(img_path).convert("RGBA")  # Asegurarse de que la imagen tenga un canal alfa
        width_percent = (uniform_width / float(img.size[0]))
        new_height = int((float(img.size[1]) * float(width_percent)))
        heights.append(new_height)

    max_height = max(heights)

    # Redimensionar y añadir márgenes a las imágenes
    columns = st.columns(len(image_paths))
    for col, img_path, height in zip(columns, image_paths, heights):
        try:
            img = Image.open(img_path).convert("RGBA")  # Asegurarse de que la imagen tenga un canal alfa
            width_percent = (uniform_width / float(img.size[0]))
            new_height = int((float(img.size[1]) * float(width_percent)))
            img = img.resize((uniform_width, new_height))
            
            # Añadir márgenes verticales con transparencia
            vertical_padding = (max_height - new_height) // 2
            img_with_padding = ImageOps.expand(img, border=(0, vertical_padding, 0, vertical_padding), fill=(0, 0, 0, 0))
            
            col.image(img_with_padding, use_column_width=True)
        except FileNotFoundError:
            st.error(f"No se encontró la imagen en la ruta: {img_path}")
        except Exception as e:
            st.error(f"Error al abrir la imagen en la ruta: {img_path}\n{e}")

    st.markdown("<h1 style='text-align: center;'>SIAPEMAD</h1>", unsafe_allow_html=True)
    st.markdown("## :electric_plug: Tabla de consumo energético [W]")

def cargar_datos_excel(file_path, sheet_name='Sheet1'):
    """Carga datos desde un archivo Excel."""
    try:
        df = pd.read_excel(io=file_path, engine='openpyxl', sheet_name=sheet_name, usecols=None, nrows=5000)
        return df
    except FileNotFoundError:
        st.error(f"No se encontró el archivo en la ruta: {file_path}")
    except Exception as e:
        st.error(f"Error al cargar los datos desde {file_path}\n{e}")
        return None

def cargar_datos(tipo_dataset, excel_files):
    """Carga los datos seleccionados y los almacena en el estado de la sesión."""
    selected_key = st.sidebar.selectbox(f"Seleccione el dataset de {tipo_dataset}", list(excel_files.keys()))
    file_path = excel_files[selected_key]
    st.session_state.selected_dataset = selected_key

    if tipo_dataset == "consumo" and st.session_state.data_consumo is None:
        df = cargar_datos_excel(file_path)
        st.session_state.data_consumo = df

    if tipo_dataset == "actividad" and st.session_state.data_actividad is None:
        df = cargar_datos_excel(file_path)
        st.session_state.data_actividad = df

    if st.sidebar.button(f"Cargar y ejecutar {tipo_dataset}"):
        df = cargar_datos_excel(file_path)
        if tipo_dataset == "actividad":
            st.session_state.data_actividad = df
        elif tipo_dataset == "consumo":
            st.session_state.data_consumo = df

    return st.session_state.data_actividad if tipo_dataset == "actividad" else st.session_state.data_consumo

def filtrar_datos_consumo(df):
    """Filtra los datos de consumo según el rango de fechas y horas seleccionado."""
    columnas_totales = [
        'Luz Pasillo', 'Luz Cocina', 'Luz Salon', 'Luz Bano', 'Luz Dormitorio',
        'Luz Entrada', 'Enchufe Salon', 'Persiana Salon', 'Puerta', 'Sensor Movimiento Salon',
        'Sensor Movimiento Pasillo', 'Enchufe Cocina', 'Persiana Salida', 'Boton', 'Temperatura',
        'Temperatura Salon', 'Temperatura Pasillo', 'Zwave', 'Porterillo', 'SmartImplant',
        'Cuarto Lavadora', 'Persiana Dormitorio', 'Descolgar', 'Luminosidad Salon', 'Luminosidad Pasillo'
    ]
    
    columnas_de_interes = [col for col in columnas_totales if col in df.columns]

    df_unique = df.drop_duplicates(subset='fecha')
    df_unique['fecha'] = pd.to_datetime(df_unique['fecha'])

    min_fecha = df_unique['fecha'].min().date()
    max_fecha = df_unique['fecha'].max().date()

    # Mensajes de depuración para verificar las fechas
    print(f"min_fecha: {min_fecha}, max_fecha: {max_fecha}")

    # Actualizar session_state con las fechas mínimas y máximas del archivo Excel
    st.session_state["fecha_inicio"] = min_fecha
    st.session_state["hora_inicio"] = pd.Timestamp("00:00:00").time()
    st.session_state["fecha_fin"] = max_fecha
    st.session_state["hora_fin"] = pd.Timestamp("23:59:59").time()

    print(f"Set default fecha_inicio: {st.session_state['fecha_inicio']}, fecha_fin: {st.session_state['fecha_fin']}")

    fecha_inicio = st.sidebar.date_input("Fecha de inicio", value=st.session_state["fecha_inicio"], min_value=min_fecha, max_value=max_fecha)
    hora_inicio = st.sidebar.time_input("Hora de inicio", value=st.session_state["hora_inicio"])
    
    fecha_fin = st.sidebar.date_input("Fecha de fin", value=st.session_state["fecha_fin"], min_value=min_fecha, max_value=max_fecha)
    hora_fin = st.sidebar.time_input("Hora de fin", value=st.session_state["hora_fin"])

    aplicar_filtro = st.sidebar.button("Aplicar Filtro")
    deshacer_filtro = st.sidebar.button("Deshacer Filtro")

    datos_filtrados = df_unique
    if aplicar_filtro:
        fecha_hora_inicio = pd.Timestamp(f"{fecha_inicio} {hora_inicio}")
        fecha_hora_fin = pd.Timestamp(f"{fecha_fin} {hora_fin}")

        if fecha_hora_inicio <= fecha_hora_fin:
            datos_filtrados = df_unique[(df_unique['fecha'] >= fecha_hora_inicio) & (df_unique['fecha'] <= fecha_hora_fin)]
            st.dataframe(datos_filtrados, use_container_width=True)
    elif deshacer_filtro:
        st.dataframe(df_unique, use_container_width=True)
    else:
        st.dataframe(df_unique, use_container_width=True)


    return columnas_de_interes, datos_filtrados, fecha_inicio, fecha_fin

def top_kpis(columnas_de_interes, datos_filtrados, fecha_inicio, fecha_fin):
    """Muestra los principales KPIs energéticos."""
    st.markdown("##")
    st.title(":bar_chart: Top KPIs Energéticos")

    valor_max_por_sensor = datos_filtrados[columnas_de_interes].max()
    valor_max_consumo = valor_max_por_sensor.max()

    left_column, right_column = st.columns(2)
    with left_column:
        st.subheader("Consumo máximo")
        st.subheader(valor_max_consumo)
    with right_column:
        st.subheader("Tiempo máximo de sensor activo")
        st.subheader(fecha_fin - fecha_inicio)

    st.markdown("---")

    hide_st_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden; }
        header {visibility: hidden; }
        </style>
        """
    st.markdown(hide_st_style, unsafe_allow_html=True)

def mostrar_consumos(datos_filtrados):
    """Muestra gráficos de consumos registrados."""
    df_seleccionado = datos_filtrados.iloc[:, 2:8]
    df_sumas = df_seleccionado.sum()

    df_bar = pd.DataFrame({
        'Sensores': df_sumas.index,
        'Suma Total': df_sumas.values
    })

    fig_consumos = px.bar(
        df_bar,
        x='Suma Total',
        y='Sensores',
        orientation="h",
        title='<b>Consumos por sensor [J]<b>',
        color_discrete_sequence=["#0083B8"] * len(df_bar),
        template="plotly_white"
    )

    # En la función mostrar_consumos
    fig_consumos.update_layout(
    font=dict(size=FONT_SIZE),  # Tamaño de letra para el texto general del gráfico
    title=dict(font=dict(size=TITLE_SIZE)),  # Tamaño de letra para el título del gráfico
    xaxis=dict(title_font=dict(size=TITLEX_SIZE), tickfont=dict(size=XAXIS_SIZE)),  # Tamaño de letra para las etiquetas del eje x
    yaxis=dict(title_font=dict(size=TITLEY_SIZE), tickfont=dict(size=YAXIS_SIZE))   # Tamaño de letra para las etiquetas del eje y
    )

    df_interpolado = datos_filtrados.interpolate(inplace=False)

    # Filtra las columnas para excluir "Unnamed: 0" y "ConsumoTotal"
    columns_to_plot = [col for col in df_interpolado.columns if col not in ['Unnamed: 0', 'fecha', 'ConsumoTotal']]

    datos_filtrados['fecha'] = pd.to_datetime(datos_filtrados['fecha'])
    
    # Crear el gráfico con Plotly Express
    fig_evolucion_consumo = px.line(
        df_interpolado,
        x='fecha',
        y=columns_to_plot,
        title='Gráfico de Líneas - Datos de Sensores',
        labels={'value': 'Potencia de Sensores [W]', 'variable': 'Sensores'},
        template='plotly_dark'
    )

    fig_bigotes = px.box(
        df_interpolado,
        y=df_interpolado.columns[2:8],
        title='Diagrama de caja',
        labels={'variable': 'Sensores', 'value': 'Valores'}
    )

    fig_evolucion_consumo.update_layout(
    font=dict(size=FONT_SIZE),  # Tamaño de letra para el texto general del gráfico
    title=dict(font=dict(size=TITLE_SIZE)),  # Tamaño de letra para el título del gráfico
    xaxis=dict(title_font=dict(size=TITLEX_SIZE), tickfont=dict(size=XAXIS_SIZE)),  # Tamaño de letra para las etiquetas del eje x
    yaxis=dict(title_font=dict(size=TITLEY_SIZE), tickfont=dict(size=YAXIS_SIZE)),
    legend=dict(font=dict(size=LEGEND_SIZE))  # Tamaño de letra para la leyenda
    )

    # Aplicar escala logarítmica al eje y
    fig_bigotes.update_layout(
    font=dict(size=FONT_SIZE),  # Tamaño de letra para el texto general del gráfico
    title=dict(font=dict(size=TITLE_SIZE)),  # Tamaño de letra para el título del gráfico
    xaxis=dict(title_font=dict(size=TITLEX_SIZE), tickfont=dict(size=XAXIS_SIZE)),  # Tamaño de letra para las etiquetas del eje x
    yaxis=dict(title_font=dict(size=TITLEY_SIZE), tickfont=dict(size=YAXIS_SIZE), type='log'),
    legend=dict(font=dict(size=LEGEND_SIZE))  # Tamaño de letra para la leyenda
    )
    
    left_colum, right_column = st.columns(2)
    left_colum.plotly_chart(fig_consumos, use_container_width=True)
    right_column.plotly_chart(fig_evolucion_consumo, use_container_width=True)

    st.markdown(
        """
        <style>
        .flex-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            width: 100%;
        }
        .plotly-chart {
            width: 80%;
            margin: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="flex-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_bigotes, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def mostrar_actividad(df_actividad):
    """Muestra el índice de actividad de los residentes."""
    st.markdown("---")
    st.markdown("##")
    st.title(":walking: Behaviour Patterns")
    activity_proc = Actividad(df_actividad).datos()

    # Definir el orden de las categorías
    categoria_orden = ['alto', 'medio', 'bajo']
    activity_proc['clasificacion'] = pd.Categorical(activity_proc['clasificacion'], categories=categoria_orden, ordered=True)

    total_count = activity_proc['clasificacion'].count()
    bajo_count = activity_proc['clasificacion'].eq('bajo').sum()
    medio_count = activity_proc['clasificacion'].eq('medio').sum()
    alto_count = activity_proc['clasificacion'].eq('alto').sum()

    bajo_percent = (bajo_count / total_count) * 100
    medio_percent = (medio_count / total_count) * 100
    alto_percent = (alto_count / total_count) * 100

    data_pie = {'Clasificación': ['Bajo', 'Medio', 'Alto'],
                'Porcentaje': [bajo_percent, medio_percent, alto_percent]}
    df_pie = pd.DataFrame(data_pie)

    # Crear el gráfico de barras asegurando el orden
    fig_barras = px.bar(activity_proc, x=activity_proc.index, y='clasificacion',
                        title='Clasificación de actividad por fecha',
                        labels={'clasificacion': 'Clasificación', 'index': 'Fecha'},
                        category_orders={'clasificacion': categoria_orden})

    fig_pie = px.pie(df_pie, values='Porcentaje', names='Clasificación',
                     title='Porcentaje de clasificación de actividad',
                     labels={'Porcentaje': 'Porcentaje', 'Clasificación': 'Clasificación'},
                     hole=0.4)
    
    # Aumentar el tamaño de letra en los gráficos
    fig_barras.update_layout(
    font=dict(size=FONT_SIZE),  # Tamaño de letra para el texto general del gráfico
    title=dict(font=dict(size=TITLE_SIZE)),  # Tamaño de letra para el título del gráfico
    xaxis=dict(title_font=dict(size=TITLEX_SIZE), tickfont=dict(size=XAXIS_SIZE)),  # Tamaño de letra para las etiquetas del eje x
    yaxis=dict(title_font=dict(size=TITLEY_SIZE), tickfont=dict(size=YAXIS_SIZE))   # Tamaño de letra para las etiquetas del eje y
    )

    fig_pie.update_layout(
    font=dict(size=FONT_SIZE),  # Tamaño de letra para el texto general del gráfico
    title=dict(font=dict(size=TITLE_SIZE)),  # Tamaño de letra para el título del gráfico
    xaxis=dict(title_font=dict(size=TITLEX_SIZE), tickfont=dict(size=XAXIS_SIZE)),  # Tamaño de letra para las etiquetas del eje x
    yaxis=dict(title_font=dict(size=TITLEY_SIZE), tickfont=dict(size=YAXIS_SIZE)),   # Tamaño de letra para las etiquetas del eje y
    legend=dict(font=dict(size=LEGEND_SIZE))  # Tamaño de letra para la leyenda
    )

    left_colum2, right_column2 = st.columns(2)
    left_colum2.plotly_chart(fig_barras, use_container_width=True)
    right_column2.plotly_chart(fig_pie, use_container_width=True)


def main():
    # Lógica para ocultar los campos de texto y el botón después de iniciar sesión
    if st.session_state.login_complete:
        encabezado()
        df_consumo = cargar_datos("consumo", excel_files_consumo)
        df_actividad = cargar_datos("actividad", excel_files_actividad)

        if df_consumo is not None:
            columnas_de_interes, datos_filtrados, fecha_inicio, fecha_fin = filtrar_datos_consumo(df_consumo)
            top_kpis(columnas_de_interes, datos_filtrados, fecha_inicio, fecha_fin)
            mostrar_consumos(datos_filtrados)

        if df_actividad is not None:
            mostrar_actividad(df_actividad)
    else:
        login()


if __name__ == "__main__":
    main()
