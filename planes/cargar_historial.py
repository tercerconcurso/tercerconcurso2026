import pandas as pd
from planes.models import HistorialPostulacion


def cargar_excel(ruta):

    df = pd.read_excel(ruta)

    # 🔥 limpiar columnas
    df.columns = df.columns.str.strip().str.lower()

    # 🔥 agrupar por rut y contar participaciones
    conteo = df.groupby('rut').size()

    for rut, veces in conteo.items():

        HistorialPostulacion.objects.update_or_create(
            rut=str(rut).strip(),
            defaults={'veces': int(veces)}
        )

    print("Carga completa")