import logging
import threading

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PracticalExercise
from .services.subtitles import generate_offline_subtitles

logger = logging.getLogger(__name__)


def _has_video(exercise):
    return bool(exercise.video_file or exercise.video_url)


def _needs_subtitles(exercise):
    return (
        not exercise.subtitle_en_file
        or not exercise.subtitle_ru_file
        or exercise.subtitle_status in {"none", "error"}
    )


def _generate_for_exercise(exercise_id):
    exercise = PracticalExercise.objects.filter(pk=exercise_id).first()
    if not exercise or not _has_video(exercise):
        return

    try:
        generate_offline_subtitles(exercise, model_size="base", generate_ru=True)
    except Exception:  # pragma: no cover - logged for operators
        logger.exception("Auto subtitle generation failed for exercise_id=%s", exercise_id)


@receiver(post_save, sender=PracticalExercise)
def auto_generate_subtitles_on_video_upload(sender, instance, created, update_fields=None, **kwargs):
    if not _has_video(instance):
        return

    if not created and update_fields is not None:
        tracked_fields = {"video_file", "video_url", "source_language", "is_active"}
        if tracked_fields.isdisjoint(set(update_fields)):
            return

    if instance.subtitle_status in {"pending", "processing"}:
        return

    if not _needs_subtitles(instance):
        return

    PracticalExercise.objects.filter(pk=instance.pk).update(
        subtitle_status="pending",
        subtitle_error="",
    )

    def _start_worker():
        thread = threading.Thread(target=_generate_for_exercise, args=(instance.pk,), daemon=True)
        thread.start()

    transaction.on_commit(_start_worker)