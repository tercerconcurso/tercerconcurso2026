def cargar_excel(ruta):
    import pandas as pd
    from planes.models import HistorialPostulacion

    df = pd.read_excel(ruta)

    # 🔥 normalizar columnas
    df.columns = df.columns.str.strip().str.lower()

    # 🔥 verificación clave
    print(df.columns)

    # 🔥 agrupar correctamente
    conteo = df.groupby('rut').size()

    # 🔥 limpiar tabla antes (opcional pero recomendable)
    HistorialPostulacion.objects.all().delete()

    registros = [
        HistorialPostulacion(
            rut=str(rut).replace(".", "").strip(),
            veces=int(veces)
        )
        for rut, veces in conteo.items()
    ]

    HistorialPostulacion.objects.bulk_create(registros)

    print("Carga completa (rápida)")