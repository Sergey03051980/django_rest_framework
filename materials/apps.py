# materials/apps.py
from django.apps import AppConfig


class MaterialsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'materials'

    def ready(self):
        """
        Метод вызывается при запуске приложения.
        Регистрируем сигналы здесь.
        """
        # Просто импортируем models.py, чтобы сигналы зарегистрировались
        import materials.models
        print("✅ Сигналы приложения materials зарегистрированы")
