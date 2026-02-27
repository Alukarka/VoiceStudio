from django.core.management.base import BaseCommand, CommandError

from exercises.models import PracticalExercise
from exercises.services.subtitles import generate_offline_subtitles


class Command(BaseCommand):
    help = "Оффлайн генерация английских и русских субтитров (VTT) для упражнений с видео."

    @staticmethod
    def _parser_has_option(parser, option_name):
        return any(option_name in action.option_strings for action in parser._actions)

    def add_arguments(self, parser):
        if not self._parser_has_option(parser, "--exercise-id"):
            parser.add_argument("--exercise-id", type=int, help="ID одного упражнения")
        if not self._parser_has_option(parser, "--model-size"):
            parser.add_argument("--model-size", default="base", help="Размер Whisper модели (tiny/base/small/...)")
        if not self._parser_has_option(parser, "--skip-ru"):
            parser.add_argument(
                "--skip-ru",
                action="store_true",
                help="Генерировать только английские субтитры без перевода на русский",
            )

    def handle(self, *args, **options):
        exercise_id = options.get("exercise_id")
        model_size = options.get("model_size")
        generate_ru = not options.get("skip_ru")

        queryset = PracticalExercise.objects.filter(is_active=True)
        if exercise_id:
            queryset = queryset.filter(id=exercise_id)

        exercises = queryset.filter(video_file__isnull=False).exclude(video_file='') | queryset.exclude(video_url='')
        exercises = exercises.distinct()

        if not exercises.exists():
            raise CommandError("Не найдено упражнений с видео для генерации субтитров.")

        for exercise in exercises:
            self.stdout.write(f"Генерация субтитров: [{exercise.id}] {exercise.title}")
            try:
                generate_offline_subtitles(exercise, model_size=model_size, generate_ru=generate_ru)
                self.stdout.write(self.style.SUCCESS(f"Готово: [{exercise.id}]"))
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"Ошибка [{exercise.id}]: {exc}"))