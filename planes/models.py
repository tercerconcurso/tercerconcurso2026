from django.db import models
from pyproj import Transformer
from django.contrib.auth.models import User

class Plan(models.Model):
    numero = models.AutoField(primary_key=True)
    nombre_agricultor = models.CharField(max_length=200)
    rut_agricultor = models.CharField(max_length=20)
    comuna = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    concurso = models.CharField(max_length=100)

    nombre_operador = models.CharField(max_length=200)
    rut_operador = models.CharField(max_length=20)
    correo_operador = models.EmailField()
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    ESTADO_ADMIN = [
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    PARTICIPACION = [
        (1, 'Primera vez'),
        (2, 'Segunda vez'),
        (3, 'Tercera vez'),
    ]

    estado_administrativo = models.CharField(
        max_length=10,
        choices=ESTADO_ADMIN,
        null=True,
        blank=True
    )

    motivo_rechazo_admin = models.TextField(
        null=True,
        blank=True
    )

    participacion_agricultor = models.IntegerField(
        choices=PARTICIPACION,
        null=True,
        blank=True
    )

    ESTADO_RECONSIDERACION = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Reconsiderado aprobado'),
        ('rechazado', 'Reconsiderado rechazado'),
    ]

    estado_reconsideracion = models.CharField(
        max_length=20,
        choices=ESTADO_RECONSIDERACION,
        null=True,
        blank=True
    )

    motivo_reconsideracion = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.numero} - {self.nombre_agricultor}"
    
    def save(self, *args, **kwargs):

        if self.comuna:
            self.comuna = self.comuna.strip().upper()

        if self.nombre_operador:
            self.nombre_operador = self.nombre_operador.strip().upper()

        if self.concurso:
            self.concurso = self.concurso.strip().upper()

        if self.sector:
            self.sector = self.sector.strip().upper()

        super().save(*args, **kwargs)

         # 🔥 FORZAR recálculo automático
        from .models import EvaluacionTecnica

        ev = EvaluacionTecnica.objects.filter(plan=self).first()
        if ev:
            ev.save()
    
class ResumenPlan(models.Model):
    plan = models.OneToOneField(Plan, on_delete=models.CASCADE)

    incentivo_practicas = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    incentivo_total = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)

    tipo_postulacion = models.CharField(max_length=100, null=True, blank=True)
    correo = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)

    rol_avaluo = models.CharField(max_length=100, null=True, blank=True)
    tenencia = models.CharField(max_length=50, null=True, blank=True)
    superficie_total = models.FloatField(null=True, blank=True)
    coordenada_norte = models.FloatField(null=True, blank=True)
    coordenada_este = models.FloatField(null=True, blank=True)
    huso = models.IntegerField(null=True, blank=True)

    @property
    def nombre_agricultor(self):
        return self.plan.nombre_agricultor

    @property
    
    def rut_agricultor(self):
        return self.plan.rut_agricultor

    @property
    def comuna(self):
        return self.plan.comuna

    @property
    def sector(self):
        return self.plan.sector
    
    @property
    def nombres_potreros(self):
        return ", ".join([
            p.nombre for p in self.plan.potreros.all()
        ])
    
    @property
    def superficie_potreros(self):
        return sum([
            p.superficie or 0 for p in self.plan.potreros.all()
        ])
    
    @property
    def detalle_potreros(self):
        return ", ".join([
            f"{p.nombre} ({p.superficie} ha)"
            for p in self.plan.potreros.all()
        ])

    @property
    def costo_calculado(self):
        costo_practicas = sum([
            p.costo or 0 for p in self.practicas.all()
        ])

    @property
    def costo_practicas(self):
        return sum([
            p.costo or 0
            for potrero in self.plan.potreros.all()
            for p in potrero.practicas.all()
        ])
    
    @property
    def costo_analisis(self):
        return sum([
            p.costo_analisis_suelo or 0
            for p in self.plan.potreros.all()
        ])


    @property
    def costo_asesoria(self):
        return sum([
            p.asesoria_plan or 0
            for p in self.plan.potreros.all()
        ])


    @property
    def costo_total_real(self):
        return (
            self.costo_practicas +
            self.costo_analisis +
            self.costo_asesoria
        )
    
    
    @property
    def estado_tecnico(self):
        ev = getattr(self.plan, 'evaluaciontecnica', None)
        return ev.estado_tecnico if ev else None


    @property
    def puntaje_tecnico(self):
        ev = getattr(self.plan, 'evaluaciontecnica', None)
        return ev.puntaje if ev else 0


    @property
    def estado_administrativo(self):
        return self.plan.estado_administrativo


    @property
    def motivo_rechazo_admin(self):
        return self.plan.motivo_rechazo_admin 
    
    @property
    def motivo_rechazo_tecnico(self):
        ev = getattr(self.plan, 'evaluaciontecnica', None)
        return ev.motivo_rechazo_tecnico if ev else None


    @property
    def estado_reconsideracion(self):
        return self.plan.estado_reconsideracion


    @property
    def motivo_reconsideracion(self):
        return self.plan.motivo_reconsideracion
    
    def save(self, *args, **kwargs):

        # 🔹 obtener porcentaje desde el PRIMER potrero
        potrero = self.plan.potreros.first()

        if potrero and potrero.porcentaje_incentivo:
            porcentaje = float(potrero.porcentaje_incentivo) / 100
        else:
            porcentaje = 0

        # 🔹 costo neto total
        costo_neto_total = sum([
            float(p.costo_neto or 0)
            for p in self.plan.potreros.all()
        ])

        # 🔥 incentivo prácticas
        incentivo_practicas = costo_neto_total * porcentaje

        # 🔹 costos adicionales
        costo_analisis = sum([
            float(p.costo_analisis_suelo or 0)
            for p in self.plan.potreros.all()
        ])

        costo_asesoria = sum([
            float(p.asesoria_plan or 0)
            for p in self.plan.potreros.all()
        ])

        # 🔥 guardar en BD
        self.incentivo_practicas = incentivo_practicas
        self.incentivo_total = float(incentivo_practicas) + float(costo_analisis) + float(costo_asesoria)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Resumen {self.plan.numero}"
    
   
class Potrero(models.Model):
    plan = models.ForeignKey(
        'Plan',
        on_delete=models.CASCADE,
        related_name='potreros'
    )

    nombre = models.CharField(max_length=100)
    superficie = models.DecimalField(max_digits=10, decimal_places=2)

    # Coordenadas UTM
    utm_este = models.DecimalField(max_digits=12, decimal_places=2)
    utm_norte = models.DecimalField(max_digits=12, decimal_places=2)
    huso = models.IntegerField(choices=[(18, '18'), (19, '19')])

    # Fechas
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_termino = models.DateField(null=True, blank=True)


    # Costos
    costo_total = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    costo_neto = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)

    porcentaje_incentivo = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    costo_analisis_suelo = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True
        )

    fecha_analisis = models.DateField(null=True, blank=True)

    asesoria_plan = models.DecimalField(
            max_digits=12,
            decimal_places=0,
            null=True,
            blank=True
    )

    # Campos calculados (guardados, pero NO calculados aquí)
    incentivo_solicitado = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.plan})"
    
    class Meta:
        ordering = ['id']
    
    def obtener_latlon(self):
        if not self.utm_este or not self.utm_norte or not self.huso:
            return None, None

        try:
            zona = f"327{self.huso}"  # Chile sur
            transformer = Transformer.from_crs(f"EPSG:{zona}", "EPSG:4326", always_xy=True)

            lon, lat = transformer.transform(float(self.utm_este), float(self.utm_norte))
            return lat, lon

        except Exception as e:
            print("ERROR TRANSFORMACION:", e)
            return None, None
        
    def clean(self):
        
        from django.core.exceptions import ValidationError

        if not self.pk:
            return

        errores = {}

        # Obtener todos los potreros del plan
        if not self.pk:
            return

        potreros = list(self.plan.potreros.all()) if self.plan_id else []

        es_primer_potrero = False

        if not self.pk and not potreros:
            es_primer_potrero = True
        elif potreros:
            es_primer_potrero = (potreros[0].pk == self.pk)

        # 🔴 VALIDACIONES SOLO PARA EL PRIMERO
        if es_primer_potrero:

            if not self.fecha_inicio:
                errores['fecha_inicio'] = "Debe ingresar fecha inicio"

            if not self.fecha_termino:
                errores['fecha_termino'] = "Debe ingresar fecha término"

            if not self.costo_total:
                errores['costo_total'] = "Debe ingresar costo total"

            if not self.costo_neto:
                errores['costo_neto'] = "Debe ingresar costo neto"

            if not self.porcentaje_incentivo:
                errores['porcentaje_incentivo'] = "Debe ingresar % incentivo"

            # ✔️ Validar análisis solo si es 2026
            if self.fecha_analisis and self.fecha_analisis.year == 2026:
                if not self.costo_analisis_suelo:
                    errores['costo_analisis_suelo'] = "Debe ingresar costo análisis 2026"

            # ✔️ asesoría obligatoria en el primero
            if not self.asesoria_plan:
                errores['asesoria_plan'] = "Debe ingresar asesoría"

        # 🔵 VALIDACIÓN GENERAL (TODOS)
        if self.fecha_inicio and self.fecha_termino:
            if self.fecha_inicio > self.fecha_termino:
                errores['fecha_termino'] = "Fecha término no puede ser menor"

        if errores:
            raise ValidationError(errores)
    
    def ver_mapa(self):
        if hasattr(self, 'latitud') and hasattr(self, 'longitud'):
            return f"https://www.google.com/maps?q={self.latitud},{self.longitud}"
        return None
                
class PracticaPotrero(models.Model):

    TIPO_PRACTICA = [
        ('fosforo', 'Fertilización fosforada'),
        ('enmienda', 'Incorporación de elementos químicos esenciales'),
        ('cubierta', 'Cubiertas vegetales'),
    ]

    SUBPRACTICA_ENMIENDA_CHOICES = [
        ('cal', 'Enmienda calcárea'),
        ('azufre', 'Azufre'),
        ('potasio', 'Potasio'),
    ]

    subtipo_enmienda = models.CharField(
        max_length=20,
        choices=SUBPRACTICA_ENMIENDA_CHOICES,
        blank=False,
        null=False
    )
    SUBTIPO_CUBIERTA = [
        ('siembra', 'Siembra'),
        ('regeneracion', 'Regeneración'),
    ]

    potrero = models.ForeignKey(
        'Potrero',
        on_delete=models.CASCADE,
        related_name='practicas'
    )

    tipo = models.CharField(max_length=20, choices=TIPO_PRACTICA)

    SUBPRACTICA_ENMIENDA_CHOICES = [
        ('cal', 'Enmienda calcárea'),
        ('azufre', 'Azufre'),
        ('potasio', 'Potasio'),
    ]

    subtipo_enmienda = models.CharField(
        max_length=20,
        choices=SUBPRACTICA_ENMIENDA_CHOICES,
        blank=True,
        null=True
    )

    subtipo_cubierta = models.CharField(
        max_length=20,
        choices=SUBTIPO_CUBIERTA,
        null=True,
        blank=True
    )

    # Datos técnicos
    nivel_inicial = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ingresar en cmol/kg (para potasio)"
    )
    nivel_final = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ingresar en cmol/kg (para potasio)"
    )


    saturacion_aluminio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ingresar % de saturación de aluminio (solo enmienda calcárea)"
    )

    resultado = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    costo = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)  # 🔴 guardar primero

        # 🔥 ENMIENDA CALCÁREA
        if self.tipo == 'enmienda' and self.subtipo_enmienda == 'cal':
            if self.saturacion_aluminio is not None and self.nivel_final is not None:
                self.resultado = self.saturacion_aluminio - self.nivel_final

        # 🔵 RESTO
        elif self.nivel_inicial is not None and self.nivel_final is not None:
            self.resultado = self.nivel_final - self.nivel_inicial

        else:
            self.resultado = None

        super().save(update_fields=['resultado'])  # 🔴 guardar resultado

    def clean(self):
        from django.core.exceptions import ValidationError

        practicas = self.potrero.practicas.exclude(pk=self.pk)

        # ❗ SOLO UNA de fósforo
        if self.tipo == 'fosforo':
            if practicas.filter(tipo='fosforo').exists():
                raise ValidationError("Solo puede existir una práctica de fósforo por potrero")

        # ❗ SOLO UNA cubierta vegetal
        if self.tipo == 'cubierta':
            if practicas.filter(tipo='cubierta').exists():
                raise ValidationError("Solo puede existir una práctica de cubierta vegetal por potrero")

        # ✔️ ELEMENTOS QUÍMICOS (pueden ser varios, pero con subtipo)
        if self.tipo == 'enmienda' and self.subtipo_enmienda == 'cal':
            if self.saturacion_aluminio is not None and self.nivel_final is not None:
                self.resultado = self.saturacion_aluminio - self.nivel_final

        # ✔️ cubierta requiere subtipo
        if self.tipo == 'cubierta':
            if not self.subtipo_cubierta:
                raise ValidationError("Debe seleccionar si es siembra o regeneración")

    def __str__(self):
        return f"{self.tipo} - {self.potrero}"     

    

class EvaluacionTecnica(models.Model):

    ESTADO_TECNICO = [
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    plan = models.OneToOneField(Plan, on_delete=models.CASCADE)

    estado_tecnico = models.CharField(
        max_length=10,
        choices=ESTADO_TECNICO,
        null=True,
        blank=True
    )

    motivo_rechazo_tecnico = models.TextField(
        null=True,
        blank=True
    )

    puntaje = models.FloatField(
        null=True,
        blank=True
    )
    def calcular_puntaje(self):

        total = 0

        total += self.puntaje_aporte_financiero()
        total += self.puntaje_fosforo()
        total += self.puntaje_potasio()
        total += self.puntaje_azufre()
        total += self.puntaje_cal()
        total += self.puntaje_participacion()
        total += self.puntaje_pradera()

        return round(total, 2)
    
    def puntaje_aporte_financiero(self):

        potrero = self.plan.potreros.first()

        if not potrero or potrero.porcentaje_incentivo is None:
            return 0

        incentivo = potrero.porcentaje_incentivo
        aporte = 100 - incentivo

        # 🔥 tipo desde concurso
        tipo = (self.plan.concurso or "").lower()

        # 🔥 mínimos según tipo
        if "peque" in tipo or "indigena" in tipo:
            minimo = 10
        elif "mediano" in tipo:
            minimo = 30
        else:
            return 0

        adicional = aporte - minimo

        if adicional <= 0:
            return 100

        puntaje = 100 + (adicional * 10)

        return min(puntaje, 400)
    
    TRAMOS_FOSFORO = [
        (5, 500),
        (10, 400),
        (15, 300),
        (20, 200),
        (999, 100),
    ]

    TRAMOS_POTASIO = [
        (0.2, 400),
        (0.3, 300),
        (0.4, 200),
        (999, 100),
    ]

    TRAMOS_AZUFRE = [
        (5, 300),
        (10, 200),
        (20, 100),
        (999, 50),
    ]

    TRAMOS_CAL = [
        (1, 100),
        (2, 200),
        (3, 300),
        (999, 400),
    ]

    TRAMOS_PRADERA = [
        (1, 40),
        (5, 100),
        (10, 200),
        (20, 300),
        (999, 400),
    ]

    def puntaje_fosforo(self):

        niveles = []

        for potrero in self.plan.potreros.all():
            for practica in potrero.practicas.all():

                if (practica.tipo or "").lower() == 'fosforo' and practica.nivel_inicial is not None:
                    niveles.append(practica.nivel_inicial)

        if not niveles:
            return 0

        nivel = min(niveles)  # 🔥 peor caso (más deficiente)

        for limite, puntaje in self.TRAMOS_FOSFORO:
            if nivel <= limite:
                return puntaje

        return 0
    
    def puntaje_potasio(self):

        for potrero in self.plan.potreros.all():
            for practica in potrero.practicas.all():

                if (
                    (practica.tipo or "").lower() == 'enmienda' and
                    (practica.subtipo_enmienda or "").lower() == 'potasio' and
                    practica.nivel_inicial
                ):

                    nivel = practica.nivel_inicial

                    for limite, puntaje in self.TRAMOS_POTASIO:
                        if nivel <= limite:
                            return puntaje

        return 0


    def puntaje_azufre(self):

        for potrero in self.plan.potreros.all():
            for practica in potrero.practicas.all():

                if (
                    (practica.tipo or "").lower() == 'enmienda' and
                    (practica.subtipo_enmienda or "").lower() == 'azufre' and
                    practica.nivel_inicial
                ):

                    nivel = practica.nivel_inicial

                    for limite, puntaje in self.TRAMOS_AZUFRE:
                        if nivel <= limite:
                            return puntaje

        return 0

    def puntaje_cal(self):

        for potrero in self.plan.potreros.all():
            for practica in potrero.practicas.all():

                if (
                    (practica.tipo or "").lower() == 'enmienda' and
                    (practica.subtipo_enmienda or "").lower() == 'cal' and
                    practica.resultado
                ):
                    mejora = practica.resultado  # ↓ aluminio

                    for limite, puntaje in self.TRAMOS_CAL:
                        if mejora <= limite:
                            return puntaje

        return 0


    def puntaje_pradera(self):

        superficie_total = 0

        for potrero in self.plan.potreros.all():
            for practica in potrero.practicas.all():

                if (practica.tipo or "").lower() == 'cubierta':
                    superficie_total += potrero.superficie or 0

        if superficie_total == 0:
            return 0

        for limite, puntaje in self.TRAMOS_PRADERA:
            if superficie_total <= limite:
                return puntaje

        return 0

    def puntaje_participacion(self):

        from planes.models import HistorialPostulacion

        rut = str(self.plan.rut_agricultor).replace(".", "").strip()

        print("RUT PLAN:", rut)
        print("HISTORIAL:", HistorialPostulacion.objects.filter(rut__iexact=rut).first())

        historial = HistorialPostulacion.objects.filter(rut__iexact=rut).first()

        veces = historial.veces if historial else 0

        # 🔥 IMPORTANTE: NO sumar 1 aquí
        if veces == 0:
            return 300
        elif veces == 1:
            return 150
        else:
            return 0
    
    def detalle_puntajes(self):

        return {
            "fosforo": self.puntaje_fosforo(),
            "potasio": self.puntaje_potasio(),
            "azufre": self.puntaje_azufre(),
            "cal": self.puntaje_cal(),
            "pradera": self.puntaje_pradera(),
            "aporte": self.puntaje_aporte_financiero(),
            "participacion": self.puntaje_participacion(),
        }


    def save(self, *args, **kwargs):

        # 🔥 calcular puntaje antes de guardar
        self.puntaje = self.calcular_puntaje()

        super().save(*args, **kwargs)
        def __str__(self):
            return f"Evaluación técnica - Plan {self.plan.numero}"   
        

class HistorialPostulacion(models.Model):
    rut = models.CharField(max_length=12)
    veces = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.rut} - {self.veces}"