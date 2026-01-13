from django.apps import AppConfig

class ThekuaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'thekua'

    def ready(self):
        import thekua.signals






