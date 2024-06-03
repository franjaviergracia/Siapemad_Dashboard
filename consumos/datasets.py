# Lista de nombres de los archivos Excel disponibles

# Determinar si estamos en entorno local o de deployment
LOCAL = False  # Cambia a False cuando despliegues en GitHub

# Definir la ruta base dependiendo del entorno
if LOCAL:
    base_url = "C:/Users/34688/Documents/CARPETAS DE TRABAJO DE JAVI/python_ws/Siapemad_Dashboard/"
else:
    base_url = "https://raw.githubusercontent.com/franjaviergracia/Siapemad_Dashboard/main/"


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

# Lista de rutas de las imágenes
image_paths = [
    "consumos/Logo_1.png",
    "consumos/Logo_2.png",
    "consumos/Logo_3.png",
    "consumos/Logo_4.png"
]
