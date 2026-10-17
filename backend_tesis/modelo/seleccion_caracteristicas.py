"""
Selección de características con ReliefF sobre las mismas variables que usa el modelo.

Uso (desde backend_tesis/modelo):
    python seleccion_caracteristicas.py [ruta/logs.csv]
Requiere: pip install skrebate
"""
import sys

import pandas as pd
from skrebate import ReliefF

from caracteristicas import cargar_logs, construir, etiqueta_heuristica
from modelo_random_forest import COLUMNAS_X

RUTA_SALIDA = 'caracteristicas_seleccionadas.csv'


def procesar_modelo(ruta=None):
    features = construir(cargar_logs(ruta))
    # PROVISIONAL (A-18): antes se usaban etiquetas aleatorias; ahora la misma etiqueta que el modelo
    y = etiqueta_heuristica(features).values
    X = features[COLUMNAS_X].astype(float).values

    print("--- Ejecutando Algoritmo RELIEF ---")
    fs = ReliefF(n_features_to_select=3, n_neighbors=min(10, len(features) - 1))
    fs.fit(X, y)

    importancia = pd.DataFrame({
        'Característica': COLUMNAS_X,
        'Peso_Relief': fs.feature_importances_,
    }).sort_values(by='Peso_Relief', ascending=False)

    print("\nRanking de Importancia de Características:")
    print(importancia.to_string(index=False))
    importancia.to_csv(RUTA_SALIDA, index=False)
    print(f"\nResultados guardados en: {RUTA_SALIDA}")


if __name__ == "__main__":
    procesar_modelo(sys.argv[1] if len(sys.argv) > 1 else None)
