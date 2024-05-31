import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
from datasets import excel_files_actividad, excel_files_consumo, image_paths
from actividad import Actividad

if "data_actividad" not in st.session_state:
    st.session_state.data_actividad = None
if "data_consumo" not in st.session_state:
    st.session_state.data_consumo = None

st.set_page_config(page_title="Métricas de SIAPEMAD",
                   page_icon=":bar_chart:",
                   layout="wide"
                   )


def encabezado():
    # Tamaño uniforme para todas las imágenes
    uniform_width = 300  # Cambia a las dimensiones que prefieras

    # Crear columnas para organizar las imágenes en una fila
    columns = st.columns(len(image_paths))

    # Mostrar cada imagen redimensionada en su columna correspondiente
    for col, img_path in zip(columns, image_paths):
        try:
            # Abrir la imagen
            img = Image.open(img_path)
            # Calcular la nueva altura para mantener la relación de aspecto
            width_percent = (uniform_width / float(img.size[0]))
            new_height = int((float(img.size[1]) * float(width_percent)))
            # Redimensionar la imagen
            img = img.resize((uniform_width, new_height))
            # Mostrar la imagen redimensionada
            col.image(img, use_column_width=True)
        except FileNotFoundError:
            st.error(f"No se encontró la imagen en la ruta: {img_path}")
        except Exception as e:
            st.error(f"Error al abrir la imagen en la ruta: {img_path}\n{e}")

    st.markdown(
        """
        <h1 style='text-align: center;'>SIAPEMAD</h1>
        """,
        unsafe_allow_html=True
    )
    st.markdown("## :electric_plug: Tabla de consumo energético [W]")

# Función para cargar datos desde un archivo Excel
def cargar_datos_excel(file_path, sheet_name='Sheet1'):
    try:
        df = pd.read_excel(io=file_path, engine='openpyxl',
                           sheet_name=sheet_name, usecols=None, nrows=5000)
        return df
    except FileNotFoundError:
        st.error(f"No se encontró el archivo en la ruta: {file_path}")
    except Exception as e:
        st.error(f"Error al cargar los datos desde {file_path}\n{e}")
        return None


def cargar_datos(tipo_dataset, excel_files):
    print("\tipo_dataset\n: ", tipo_dataset, "\n")
    print("\nexcel_files\n: ", excel_files, "\n")
    print("Entro en la carga de datos")
    selected_key = st.sidebar.selectbox(
        f"Seleccione el dataset de {tipo_dataset}",  list(excel_files.keys()))
    file_path = excel_files[selected_key]
    st.session_state.selected_dataset = selected_key

    if st.session_state.data_consumo is None and tipo_dataset == "consumo":
        df = cargar_datos_excel(excel_files["Consumo 1"])
        print("\nDATOS CARGADOS DE CONSUMO\n")
        st.session_state.data_consumo = df
        if df is not None:
            # Almacena el DataFrame en el estado de la sesión
            st.session_state[f"{tipo_dataset}_df"] = df

    # Es la primera carga por defecto, del dataset 1
    if st.session_state.data_actividad is None and tipo_dataset == "actividad":
        df = cargar_datos_excel(excel_files["Actividad 1"])
        print("\nDATOS CARGADOS DE ACTIVIDAD\n")
        st.session_state.data_actividad = df
        if df is not None:
            # Almacena el DataFrame en el estado de la sesión
            st.session_state[f"{tipo_dataset}_df"] = df



    # Cargas solicitadas a través de las pulsaciones de los botones
    elif st.sidebar.button(f"Cargar y ejecutar {tipo_dataset}"):
        if st.session_state.selected_dataset not in st.session_state or st.session_state[f"{tipo_dataset}_df"] is None:
            print("Estoy en la parte de carga de carga nueva")
            df = cargar_datos_excel(file_path)
            if tipo_dataset == "actividad":
                st.session_state.data_actividad = df
            elif tipo_dataset == "consumo":
                st.session_state.data_consumo = df

            if df is not None:
                # Almacena el DataFrame en el estado de la sesión
                st.session_state[f"{tipo_dataset}_df"] = df
        else:
            # Recupera el DataFrame del estado de la sesión
            print("Estoy en la parte de carga de carga previa")
            
            df = st.session_state[f"{tipo_dataset}_df"]
            print(df)
    else: 
        # df = st.session_state.data
        print("Entro else")
    return df


def filtrar_datos_consumo(df):
    columnas_totales = ['Luz Pasillo', 'Luz Cocina', 'Luz Salon', 'Luz Bano', 'Luz Dormitorio', 'Luz Entrada', 'Enchufe Salon', 'Persiana Salon', 'Puerta', 'Sensor Movimiento Salon', 'Sensor Movimiento Pasillo', 'Enchufe Cocina',
                        'Persiana Salida', 'Boton', 'Temperatura', 'Temperatura Salon', 'Temperatura Pasillo', 'Zwave', 'Porterillo', 'SmartImplant', 'Cuarto Lavadora', 'Persiana Dormitorio', 'Descolgar', 'Luminosidad Salon', 'Luminosidad Pasillo']
    columnas_de_interes = [
        col for col in columnas_totales if col in df.columns]

    df_unique = df.drop_duplicates(subset='fecha')

    # Convertir a datetime
    df_unique.loc[:, 'fecha']  = pd.to_datetime(df_unique['fecha'])
    # Rango mínimo y máximo de fechas´
    
    min_fecha = df['fecha'].min().date()  # Solo la parte de fecha
    max_fecha = df['fecha'].max().date()
    
    # Inicializar el estado de la sesión si no existe
    # if "fecha_inicio" not in st.session_state:  # or cargar_datos_consumo_button
    st.session_state["fecha_inicio"] = min_fecha
    st.session_state["hora_inicio"] = pd.Timestamp("00:00:00").time()
    st.session_state["fecha_fin"] = max_fecha
    st.session_state["hora_fin"] = pd.Timestamp("23:59:59").time()

    # ---- SIDEBAR ----

    # Verificar que los valores por defecto estén dentro del rango
    fecha_inicio = st.sidebar.date_input(
        "Fecha de inicio", value=st.session_state["fecha_inicio"], min_value=min_fecha, max_value=max_fecha)
    hora_inicio = st.sidebar.time_input(
        "Hora de inicio", value=st.session_state["hora_inicio"])
    fecha_fin = st.sidebar.date_input(
        "Fecha de fin", value=st.session_state["fecha_fin"], min_value=min_fecha, max_value=max_fecha)
    hora_fin = st.sidebar.time_input(
        "Hora de fin", value=st.session_state["hora_fin"])

    # Si se hace clic en "Aplicar Filtro", se filtra el DataFrame por el rango seleccionado
    aplicar_filtro = st.sidebar.button("Aplicar Filtro")
    # Botón para deshacer el filtro aplicado
    deshacer_filtro = st.sidebar.button("Deshacer Filtro")

    datos_filtrados = df_unique
    if aplicar_filtro:
        # Combinar fecha y hora para obtener el rango completo de tiempo
        fecha_hora_inicio = pd.Timestamp(fecha_inicio).replace(
            hour=hora_inicio.hour,
            minute=hora_inicio.minute,
            second=hora_inicio.second
        )

        fecha_hora_fin = pd.Timestamp(fecha_fin).replace(
            hour=hora_fin.hour,
            minute=hora_fin.minute,
            second=hora_fin.second
        )

        if fecha_hora_inicio <= fecha_hora_fin:
            datos_filtrados = df_unique[
                (df_unique['fecha'] >= fecha_hora_inicio) & (
                    df_unique['fecha'] <= fecha_hora_fin)
            ]
            # Mostrar el resultado
            st.dataframe(datos_filtrados, use_container_width=True)

    elif deshacer_filtro:
        st.dataframe(df_unique, use_container_width=True)

    else:
        datos_filtrados = df_unique
        st.dataframe(df_unique, use_container_width=True)

    
    return columnas_de_interes, datos_filtrados, fecha_inicio, fecha_fin


def top_kpis(columnas_de_interes, datos_filtrados, fecha_inicio, fecha_fin):
    # ---- MAINPAGE ----
    st.markdown("##")
    st.title(":bar_chart: Top KPIs Energéticos")

    # TOP KPI's
    valor_max_por_sensor = datos_filtrados[columnas_de_interes].max()
    valor_max_consumo = valor_max_por_sensor.max()

    # AQUÍ DEBO PONER EL CÓDIGO CON LOS PRINCIPALES KPIs

    left_column, right_column = st.columns(2)
    with left_column:
        st.subheader("Consumo máximo")
        st.subheader(valor_max_consumo)
    with right_column:
        st.subheader("Tiempo máximo de sensor activo")
        st.subheader(fecha_fin-fecha_inicio)

    st.markdown("---")

    # ----HIDE STREAMLIT STYLE ----
    hide_st_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden; }
        header{visibility: hidden; }
        </style>
        """
    st.markdown(hide_st_style, unsafe_allow_html=True)

def mostrar_consumos(datos_filtrados):
    # [BAR CHART] CONSUMOS REGISTRADOS
    df_seleccionado = datos_filtrados.iloc[:, 2:8]

    # Sumar cada columna de forma independiente
    df_sumas = df_seleccionado.sum()

    # Crear un DataFrame para el gráfico de barras
    df_bar = pd.DataFrame({
        'Sensores': df_sumas.index,  # Nombres de las columnas
        'Suma Total': df_sumas.values  # Valores sumados
    })

    fig_consumos = px.bar(
        df_bar,
        x='Suma Total',  # Eje X
        y='Sensores',  # Eje Y
        orientation="h",
        title='<b>Consumos por sensor [J]<b>',
        color_discrete_sequence=["#0083B8"] * len(df_bar),
        template="plotly_white"
    )
    df_interpolado = datos_filtrados.interpolate(inplace=False)

    # Gráfico de consumos
    datos_filtrados['fecha'] = pd.to_datetime(datos_filtrados['fecha'])
    fig_evolucion_consumo = px.line(
        df_interpolado,
        x='fecha',  # La columna de fechas
        # Todas las demás columnas (datos de sensores)
        y=df_interpolado.columns[2:8],
        title='Gráfico de Líneas - Datos de Sensores',
        # Etiquetas personalizadas
        labels={'value': 'Potencia de Sensores [W]', 'variable': 'Sensores'},
        template='plotly_dark'  # Configuración visual del gráfico (opcional)
    )

    # Gráfico de bigotes
    fig_bigotes = px.box(
        df_interpolado,
        y=df_interpolado.columns[2:8],  # Ajusta según las columnas de datos
        title='Diagrama de caja',
        # Personaliza etiquetas
        labels={'variable': 'Sensores', 'value': 'Valores'}
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
            width: 80%;  # Ajusta este valor según necesites
            margin: auto;  # Esto asegura que el gráfico esté centrado en el div
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="flex-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_bigotes, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def mostrar_actividad(df_actividad):
    # ---- PARTE DEL DASHBOARD ORIENTADA A MOSTRAR EL ÍNDICE DE ACTIVIDAD DE LOS RESIDENTES ----
    st.markdown("---")
    st.markdown("##")
    st.title(":walking: Behaviour Patterns")

    activity_proc = Actividad(df_actividad).datos()

    # Calcular los porcentajes de cada clasificación
    total_count = activity_proc['clasificacion'].count()
    bajo_count = activity_proc['clasificacion'].eq('bajo').sum()
    medio_count = activity_proc['clasificacion'].eq('medio').sum()
    alto_count = activity_proc['clasificacion'].eq('alto').sum()

    bajo_percent = (bajo_count / total_count) * 100
    medio_percent = (medio_count / total_count) * 100
    alto_percent = (alto_count / total_count) * 100

    # Data pie
    data_pie = {'Clasificación': ['Bajo', 'Medio', 'Alto'],
            'Porcentaje': [bajo_percent, medio_percent, alto_percent]}
    df_pie = pd.DataFrame(data_pie)

    # Crear un gráfico de barras con Plotly Express
    fig_barras = px.bar(activity_proc, x=activity_proc.index, y='clasificacion',
                title='Clasificación de actividad por fecha',
                labels={'clasificacion': 'Clasificación', 'index': 'Fecha'})

    # Gráfico de tipo tarta
    fig_pie = px.pie(df_pie, values='Porcentaje', names='Clasificación',
                title='Porcentaje de clasificación de actividad',
                labels={'Porcentaje': 'Porcentaje', 'Clasificación': 'Clasificación'},
                hole=0.4)

    # Mostrar el gráfico
    left_colum2, right_column2 = st.columns(2)
    left_colum2.plotly_chart(fig_barras, use_container_width=True)
    right_column2.plotly_chart(fig_pie, use_container_width=True)


def main():
    encabezado()

    df_consumo = cargar_datos("consumo", excel_files_consumo)
    df_actividad = cargar_datos("actividad", excel_files_actividad)
    if df_consumo is not None:
        columnas_de_interes, datos_filtrados, fecha_inicio, fecha_fin = filtrar_datos_consumo(
            df_consumo)
        top_kpis(columnas_de_interes, datos_filtrados, fecha_inicio, fecha_fin)
    if df_consumo is not None:
        mostrar_consumos(df_consumo)
    if df_actividad is not None:
        mostrar_actividad(df_actividad)


if __name__ == "__main__":
    main()
