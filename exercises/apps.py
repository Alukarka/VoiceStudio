import logging
from importlib import import_module

from django.apps import AppConfig

logger = logging.getLogger(__name__)

class ExercisesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exercises'

    def ready(self):
        try:
            import_module('exercises.signals')
        except ModuleNotFoundError:
            logger.warning(
                'Модуль exercises.signals не найден. Автогенерация субтитров отключена.'
            )
