from django.apps import AppConfig


class PlanesConfig(AppConfig):
    name = 'planes'

def ready(self):
    import planes.signals
