
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Input, Dense, Lambda, LSTM, Masking
import tensorflow.keras.backend as K
from keras.models import Sequential
from keras.layers import LSTM, Dense, Masking, Dropout
from keras.regularizers import l2
from sklearn.pipeline import Pipeline
from datetime import datetime, timedelta
class Anomalias:

    def __init__(self) -> None:
        pass

    def preprocessFileData(self, filePath, outputPath):
        # Leer el archivo CSV
        df = pd.read_excel(filePath, header=0)
        

        # Convertir la columna 'event-time' a formato datetime
        df['event-datetime'] = pd.to_datetime(df['event-time'], format='%H:%M:%S', errors='coerce')

        # Eliminar filas con valores de fecha nulos (valores vacíos)
        df = df.dropna(subset=['event-datetime', "event-id"])

        # Inicializar la variable para almacenar la fecha del día anterior
        fecha_anterior = None

        # Lista para almacenar las secuencias por día
        secuencias = []
        
        days = 0
        # Recorrer los datos para agruparlos por día
        for _, row in df.iterrows():
            if fecha_anterior is None or row['event-datetime'].time() > fecha_anterior.time():
                # Crear una nueva secuencia para el nuevo día
                nueva_secuencia = {
                    'fecha': row['event-datetime'].date() - timedelta(days=days),
                    'eventos': [row.to_dict()]  # Convertir la fila a un diccionario y añadirlo a los datos del día
                }
                days += 1
                secuencias.append(nueva_secuencia)
            else:
                # Agregar la fila al día actual en la secuencia
                secuencias[-1]['eventos'].append(row.to_dict())

            fecha_anterior = row['event-datetime']


        # Añadi la columna 'full-date' a cada evento en las secuencias
        for secuencia in secuencias:
            for evento in secuencia['eventos']:
                fecha = secuencia['fecha'].strftime('%Y-%m-%d')  # Convertir la fecha a formato de cadena YYYY-MM-DD
                tiempo = evento['event-time']  # Obtener el valor de tiempo de la columna 'event-time'
                evento['full-date'] = f"{fecha} {tiempo}"

        # Convertir la lista de secuencias de nuevo a un DataFrame
        df_with_full_date = pd.concat([pd.DataFrame(secuencia['eventos']) for secuencia in secuencias], ignore_index=True)
        # Eliminar la columna 'event-datetime' del DataFrame
        df_with_full_date.drop(columns=['event-datetime'], inplace=True)

        # Guardar el DataFrame modificado en un nuevo archivo CSV
        df_with_full_date.to_csv(outputPath, index=False)

    def loadData(self, filePath):
        # Cargar el archivo CSV
        archivo_csv = filePath
        df = pd.read_csv(archivo_csv, header=0)  # Indicar que la primera fila es la cabecera

        # Convertir la columna 'event-time' a formato datetime
        df['intervalo'] = pd.to_datetime(df['intervalo'], errors='coerce')

        # Eliminar filas con valores de fecha nulos (valores vacíos)
        df = df.dropna(subset=['intervalo'])

        # Extraer solo la fecha de la columna 'event-time'
        df['date'] = df['intervalo'].dt.date

        # Agrupar por la fecha y crear secuencias
        secuencias = []
        for fecha, grupo in df.groupby('date'):
            secuencia = {
                'date': fecha,
                'events': grupo.to_dict('records')  # Convertir cada grupo a un diccionario
            }
            secuencias.append(secuencia)
        
        return secuencias

    def resumeDataByIntervalsAndEventIds(self, filePath, outputPath, intervalSec):
        # Cargar el archivo CSV
        df = pd.read_csv(filePath, header=0)
        print(df)
        # Convertir la columna 'full-date' a tipo datetime
        df['full-date'] = pd.to_datetime(df['event-time'])

        # Ordenar por fecha descendente
        df = df.sort_values(by='full-date', ascending=False)

        # Obtener la fecha más reciente y la fecha más lejana en el archivo
        fecha_mas_reciente = df.iloc[0]['full-date']
        fecha_mas_lejana = df.iloc[-1]['full-date']

        # Crear una lista de intervalos de x segundos desde las (00:00:00-secs) hasta las 00:00:00 del día más reciente
        intervalos = []
        fecha_inicial = datetime.combine(fecha_mas_reciente.date(), datetime.strptime('00:00:00', '%H:%M:%S').time()) - timedelta(seconds=intervalSec)
        fecha_final = datetime.combine(fecha_mas_lejana.date(), datetime.strptime('00:00:00', '%H:%M:%S').time())

        while fecha_inicial >= fecha_final:
            intervalos.append(fecha_inicial.strftime('%Y-%m-%d %H:%M:%S'))
            fecha_inicial -= timedelta(seconds=intervalSec)

        # Crear un diccionario para almacenar los conteos de eventos por intervalo
        conteos_por_intervalo = {'intervalo': [], 'fecha_completa': []}
        unique_event_ids = df['event-id'].unique()
        for event_id in unique_event_ids:
            conteos_por_intervalo[event_id] = []

        # Iterar sobre los intervalos y contar los eventos del intervalo superior para cada uno
        for intervalo in intervalos:
            fecha_inferior = datetime.strptime(intervalo, '%Y-%m-%d %H:%M:%S')
            fecha_superior = fecha_inferior + timedelta(seconds=intervalSec)
            eventos_en_intervalo = df[(df['full-date'] >= fecha_inferior) & (df['full-date'] < fecha_superior)]
            conteo_eventos = eventos_en_intervalo['event-id'].value_counts().to_dict()
            conteos_por_intervalo['intervalo'].append(intervalo)
            conteos_por_intervalo['fecha_completa'].append(fecha_inferior)
            print(conteo_eventos)
            for event_id in unique_event_ids:
                print(str(event_id)+"----"+str(conteo_eventos.get(event_id, 0)))
                conteos_por_intervalo[event_id].append(conteo_eventos.get(event_id, 0))

        # Crear DataFrame a partir del diccionario
        df_resumido = pd.DataFrame(conteos_por_intervalo)

        # Guardar el DataFrame resultante en un nuevo archivo CSV
        df_resumido.to_csv(outputPath, index=False)



    def prepareDataForLSTMInput(self,df_eventos_preprocesados_total_pp):
        # Suponiendo que tu matriz se llama 'matriz' y tiene la forma (259200, 1010)
        matriz = df_eventos_preprocesados_total_pp

        print("Longitud total:" ,df_eventos_preprocesados_total_pp.shape[0])

        # Número de filas en cada submatriz
        filas_por_submatriz = len(self.secuencias[0]["events"])

        # Calcula el número total de submatrices
        num_submatrices = matriz.shape[0] // filas_por_submatriz

        # Crea una lista para almacenar las submatrices
        lista_matrices = []

        # Divide la matriz en submatrices de 5670 filas
        for i in range(num_submatrices):
            inicio = i * filas_por_submatriz
            fin = inicio + filas_por_submatriz
            submatriz = matriz[inicio:fin, :]
            lista_matrices.append(submatriz)

        # Si el número total de filas no es divisible exactamente por 5670,
        # puedes agregar las filas restantes a una submatriz adicional
        resto = matriz.shape[0] % filas_por_submatriz
        if resto > 0:
            print("algo pasa, resto > 0")
            submatriz_resto = matriz[-resto:, :]
            lista_matrices.append(submatriz_resto)

        # Ahora la lista 'lista_matrices' contendrá todas las submatrices
        # Imprime la longitud de la lista para obtener el número de submatrices
        print("Número de submatrices:", len(lista_matrices))

        day_events_len = lista_matrices[0].shape[0]
        caracteristics_len = lista_matrices[0].shape[1]

        # Convertir lista_matrices a un arreglo numpy
        datos_numpy = np.array(lista_matrices)

        # Reformatar los datos para que tengan la forma (num_muestras, timesteps, features)
        datos_reshape = datos_numpy.reshape(datos_numpy.shape[0], -1, datos_numpy.shape[-1])

        return datos_reshape, day_events_len, caracteristics_len

    def preprocess_events(self,events):
        # Calcular el número de segundos transcurridos desde la medianoche
        events['seconds_since_midnight'] = events['event-interval'].dt.hour * 3600 + events['event-interval'].dt.minute * 60 + events['event-interval'].dt.second
        
        columnas = list(events.keys())
        # Quitar las dos primeras columnas ('intervalo' y 'fecha_completa')
        events_cols = columnas[2:-3]

        # Definir las columnas numéricas y categóricas
        numeric_cols = ['seconds_since_midnight'] + events_cols
        
        
        # Pipeline para el preprocesamiento numérico
        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        # Aplicar el preprocesamiento a la columna categórica
        processed_numeric = numeric_transformer.fit_transform(events[numeric_cols])

        # Convertir las columnas de eventos a matriz dispersa
        # processed_event_cols = events[events_cols].values

        # Concatenar la columna procesada categórica con la columna numérica
        # processed_events = hstack(processed_numeric)
        
        return processed_numeric

    def preprocessData(self, sec_eventos):
        # Crear un DataFrame con los eventos de ejemplo
        df_eventos = sec_eventos
        df_eventos_preprocesados_total = []

        for row in df_eventos:
            df_eventos_day = pd.DataFrame(row)
            for idx, event in df_eventos_day.iterrows():
                # Convertir el tiempo a formato datetime
                event['event-interval'] = pd.to_datetime(event['intervalo'], format='%H:%M:%S')
                # df_eventos_preprocesados_day.append(event)
                df_eventos_preprocesados_total.append(event)

        df_eventos_preprocesados_total_df = pd.DataFrame(df_eventos_preprocesados_total)
        # Preprocesar los eventos
        df_eventos_preprocesados_total_pp = self.preprocess_events(df_eventos_preprocesados_total_df)
        return df_eventos_preprocesados_total_pp
    
    def getAnomalias(self):
        # Método para obtener la lista de anomalías detectadas
        vivienda = "YH-00052916"
        self.secuencias = None
        self.preprocessFileData(f'./data/entrada/{vivienda}-CRUDO.xlsx',f'./data/entrada/{vivienda}-CRUDO_with_date.csv')
        self.resumeDataByIntervalsAndEventIds(f".\data\entrada\{vivienda}-CRUDO_with_date.csv", f"./data/salida/{vivienda}-CRUDO_salida.csv", 60*60*24)  # Ejemplo: Intervalos de 24h.
        self.secuencias = self.loadData(f'./data/salida/{vivienda}-CRUDO_salida.csv')
        print("Longitud de las secuencias:", len(self.secuencias))
        sec_eventos = []
        for sec in self.secuencias:
            sec_eventos.append(sec["events"])

        df_eventos_preprocesados_total_pp = self.preprocessData(sec_eventos)

        datos_reshape, day_events_len, caracteristics_len = self.prepareDataForLSTMInput(df_eventos_preprocesados_total_pp)
        print("Número de días: ", datos_reshape.shape[0])
        print("Número de eventos por día: ", day_events_len)
        print("Número de características por evento: ", caracteristics_len)

        # Definir la arquitectura del modelo
        model = Sequential()
        model.add(Masking(mask_value=0.0))   
        model.add(LSTM(256, return_sequences=True, kernel_regularizer=l2(0.01)))
        model.add(Dropout(0.2))
        model.add(LSTM(128, return_sequences=True, kernel_regularizer=l2(0.01)))
        model.add(Dropout(0.2))
        model.add(Dense(caracteristics_len, kernel_regularizer=l2(0.01)))

        model.compile(loss='mse', optimizer='adam')

        # Entrenar el modelo para la reconstrucción de secuencias
        model.fit(datos_reshape, datos_reshape, epochs=3000, verbose=1)
        import joblib
        joblib.dump(model, f"model_{vivienda}-CRUDO.pkl")

        # Reconstruir secuencias de entrenamiento
        secuencias_reconstruidas7 = model.predict(datos_reshape)

        # Calcular error de reconstrucción para cada secuencia
        errores_reconstruccion7 = np.mean(np.abs(datos_reshape - secuencias_reconstruidas7), axis=(1, 2))

        # Definir umbral de anomalía (por ejemplo, el percentil 95 de los errores de reconstrucción)
        umbral_anomalia7 = np.percentile(errores_reconstruccion7, 90)
        # umbral_anomalia = 0.15

        # Identificar secuencias anómalas
        secuencias_anomalas7 = [secuencia for secuencia, error in zip(self.secuencias, errores_reconstruccion7) if error > umbral_anomalia7]

        self.anomalias = []

        # Mostrar secuencias anómalas
        print('Secuencias Anómalas: ', len(secuencias_anomalas7))
        for i, secuencia_anomala in enumerate(secuencias_anomalas7):
            print(f'Anomalía {i + 1}: {secuencia_anomala}')
            self.anomalias.append(secuencia_anomala)
        return self.anomalias


   
if __name__ == "__main__":
    anoma = Anomalias()
    anomalias = anoma.getAnomalias()
