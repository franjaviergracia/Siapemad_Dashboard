import pandas as pd
import numpy as np

class Actividad():

    def __init__(self,dataframe) -> None:
        self.df=dataframe

    #Procesa el excel para calcular la actividad diaria. Param: dataframe-> Objeto dataframe con los datos
    def datos(self):

        self.__procesar__()
        actividad=self.__actividad__()

        return actividad

    #Elimina datos irrelevantes o faltantes
    def __procesar__(self):
        print("Chavo este es el df", self.df)
        self.df["marquee-text"]=self.df["marquee-text"].astype(str)
        self.df=self.df.drop(columns=["ng-star-inserted src", "event-source-type", "Unnamed: 36"], errors='ignore')
        self.df=self.df.dropna(axis=1, how="all")
        self.df = self.df[~(self.df['marquee-text'].str.contains('State', na=False))]
        self.df = self.df[~(self.df['marquee-text'].str.contains('Control', na=False))]
        self.df = self.df[~(self.df['marquee-text 3'].str.contains('-', na=False))]
        self.df = self.df[~(self.df['marquee-text 2'].str.contains('Luminosidad', na=False))]
        self.df = self.df[~(self.df['marquee-text 2'].str.contains('red', na=False))]
        self.df = self.df[~(self.df['marquee-text 2'].str.contains('vecinos', na=False))]
        self.df=self.df[~self.df['marquee-text'].str.contains('W')]
        self.df=self.df[~self.df['marquee-text'].str.contains('°C')]
        self.df=self.df.drop(columns=["marquee-text", "marquee-text 2", "marquee-text 3"], errors='ignore')
    
    #Calcula la actividad
    def __actividad__(self):
        
        #Pivota el dataset con la fecha y hora como index agrupando por dias y los sensores como columnas
        self.df['event-time'] = pd.to_datetime(self.df['event-time'])
        self.df=self.df.pivot_table(index=self.df['event-time'].dt.date, columns='event-id', aggfunc='size', fill_value=0)
        self.df.index= pd.to_datetime(self.df.index)

        #Suma para cada dia el numero de veces que se activa cada sensor para obtener la actividad total por dia
        actividad_dia=pd.DataFrame(self.df.sum(axis=1))
        print(actividad_dia)
        actividad_dia.rename(columns={"0":"Actividad"},inplace=True)

        #Toma una muestra para calcular el nivel de actividad medio
        sample = actividad_dia.sample(frac=0.3, random_state=1)

        mean_activity = sample.mean()
        std_dev = sample.std()  # Desviacion estandar de la actividad en la muestra
        margin = 0.5  # Margen alrededor de la media, ajusta segun lo desees
        lower_bound = mean_activity - margin * std_dev #Umbral de baja actividad
        upper_bound = mean_activity + margin * std_dev #Umbral de alta actividad

        #print(f"Media de la actividad:{mean_activity}")
        #print(f"Margenes:{lower_bound}, {upper_bound}")

        #Se clasifica cada dia en tres niveles de activacion: alto, medio y bajo
        actividad_dia['clasificacion'] = np.where(actividad_dia > upper_bound, 'alto', np.where(actividad_dia < lower_bound, 'bajo', 'medio'))
        actividad_dia=actividad_dia.drop(columns=[0])
        return actividad_dia
      