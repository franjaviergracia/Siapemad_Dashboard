import streamlit as st
# Lista de nombres de los archivos Excel disponibles

# Determinar si estamos en entorno local o de deployment
LOCAL = True  # Cambia a False cuando despliegues en GitHub

# Definir la ruta base dependiendo del entorno
if LOCAL:
    base_url = "C:/Users/CTM40/Desktop/SIAPEMAD/Siapemad_Dashboard/"
    user1 = "user1"
    pass1 = "123"
else:
    base_url = "https://raw.githubusercontent.com/franjaviergracia/Siapemad_Dashboard/main/"
    user1 = st.secrets["secrets"]["USER1"]
    pass1 = st.secrets["secrets"]["PASS1"]


excel_files_consumo = {
    "Consumo 1": base_url + "consumos/dataset_consumo_YH-00049797.xlsx",
    "Consumo 2": base_url + "consumos/dataset_consumo_YH-00052712.xlsx",
    "Consumo 3": base_url + "consumos/dataset_consumo_YH-00052886.xlsx",
    "Consumo 4": base_url + "consumos/dataset_consumo_YH-00052887.xlsx",
    "Consumo 5": base_url + "consumos/dataset_consumo_YH-00052900.xlsx",
    "Consumo 6": base_url + "consumos/dataset_consumo_YH-00052916.xlsx",
    "Consumo 7": base_url + "consumos/dataset_consumo_YH-00052918.xlsx",
    "Consumo 8": base_url + "consumos/dataset_consumo_YH-00052920.xlsx",
    "Consumo 9": base_url + "consumos/dataset_consumo_YH-00052926.xlsx",
    "Consumo 10":base_url +  "consumos/dataset_consumo_YH-00052927.xlsx",
    "Consumo 11":base_url +  "consumos/dataset_consumo_YH-00052930.xlsx",
    "Consumo 12":base_url +  "consumos/dataset_consumo_YH-00052931.xlsx"

}

excel_files_actividad = {
    "Actividad 1": base_url +"actividades/YH-00049797.xlsx",
    "Actividad 2": base_url +"actividades/YH-00052886.xlsx",
    "Actividad 3": base_url +"actividades/YH-00052887.xlsx",
    "Actividad 4": base_url +"actividades/YH-00052916.xlsx",
    "Actividad 5": base_url +"actividades/YH-00052927.xlsx",
    "Actividad 6": base_url +"actividades/YH-00052931.xlsx",
}

modelos = {
    "Actividad 1": base_url +"modelos/YH-00049797.xlsx",
    "Actividad 2": base_url +"modelos/YH-00052886.xlsx",
    "Actividad 3": base_url +"modelos/YH-00052887.xlsx",
    "Actividad 4": base_url +"modelos/YH-00052916.xlsx",
    "Actividad 5": base_url +"modelos/YH-00052927.xlsx",
    "Actividad 6": base_url +"modelos/YH-00052931.xlsx",
}

# Lista de rutas de las imágenes
image_paths = [
    "logotipos/Logo_1.png",
    "logotipos/Logo_2.png",
    "logotipos/Logo_3.png",
    "logotipos/Logo_4.png"
]
