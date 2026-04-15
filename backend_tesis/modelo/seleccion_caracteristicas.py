import pandas as pd
import numpy as np
from skrebate import ReliefF
from sklearn.preprocessing import LabelEncoder
import os


ruta_datos = os.path.join('..', 'datos', 'log_actividad.csv')
ruta_salida = 'caracteristicas_seleccionadas.csv'

def procesar_modelo():
    # 2. Carga de datos
    if not os.path.exists(ruta_datos):
        print(f"Error: No se encontró el archivo en {ruta_datos}")
        return

    df = pd.read_csv(ruta_datos)
    df['fecha'] = pd.to_datetime(df['fecha'])

    print("--- Transformando Logs en Características ---")

    # 3. Ingeniería de características
    features = df.groupby('usuario').agg(
        total_acciones=('id', 'count'),
        creaciones_clase=('accion', lambda x: (x == 'creó_clase').sum()),
        errores=('detalle', lambda x: x.str.contains('Error', case=False).sum()),
        uso_protected=('detalle', lambda x: x.str.contains('protected', case=False).sum()),
        exitos_compilacion=('detalle', lambda x: x.str.contains('Éxito', case=False).sum())
    )

    # Calculamos el tiempo total de la sesión en minutos
    tiempos = df.groupby('usuario')['fecha'].agg(['min', 'max'])
    features['tiempo_sesion_min'] = (tiempos['max'] - tiempos['min']).dt.total_seconds() / 60

    # 4. Generación de etiquetas sintéticas (Solo para la prueba de 35 usuarios)
    # En un escenario real, aquí tendrías la calificación del examen.
    # Simulamos: 0=Bajo, 1=Medio, 2=Alto
    np.random.seed(42)
    features['rendimiento'] = np.random.choice([0, 1, 2], size=len(features))

    # 5. Aplicación del ALGORITMO RELIEF
    print("--- Ejecutando Algoritmo RELIEF ---")
    
    X = features.drop('rendimiento', axis=1).values
    y = features['rendimiento'].values
    nombres_columnas = features.drop('rendimiento', axis=1).columns

    # Inicializamos ReliefF (buscamos los vecinos más cercanos para ponderar importancia)
    fs = ReliefF(n_features_to_select=3, n_neighbors=10)
    fs.fit(X, y)

    # Creamos un ranking de importancia
    importancia = pd.DataFrame({
        'Característica': nombres_columnas,
        'Peso_Relief': fs.feature_importances_
    }).sort_values(by='Peso_Relief', ascending=False)

    print("\nRanking de Importancia de Características:")
    print(importancia)

    # 6. Guardar resultados
    importancia.to_csv(ruta_salida, index=False)
    print(f"\nResultados guardados en: {ruta_salida}")

if __name__ == "__main__":
    procesar_modelo()