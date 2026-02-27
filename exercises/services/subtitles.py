import tempfile
import urllib.request
from pathlib import Path

from django.core.files.base import ContentFile


SUPPORTED_TRANSLATOR_CODES = {
    'af', 'sq', 'am', 'ar', 'hy', 'as', 'ay', 'az', 'bm', 'eu', 'be', 'bn', 'bho', 'bs', 'bg',
    'ca', 'ceb', 'ny', 'zh-cn', 'zh-tw', 'co', 'hr', 'cs', 'da', 'dv', 'doi', 'nl', 'en', 'eo',
    'et', 'ee', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gn', 'gu', 'ht', 'ha', 'haw',
    'iw', 'hi', 'hmn', 'hu', 'is', 'ig', 'ilo', 'id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km',
    'rw', 'gom', 'ko', 'kri', 'ku', 'ckb', 'ky', 'lo', 'la', 'lv', 'ln', 'lt', 'lg', 'lb', 'mk',
    'mai', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mni-mtei', 'lus', 'mn', 'my', 'ne', 'no', 'or',
    'om', 'ps', 'fa', 'pl', 'pt', 'pa', 'qu', 'ro', 'ru', 'sm', 'sa', 'gd', 'nso', 'sr', 'st',
    'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'tt', 'te', 'th',
    'ti', 'ts', 'tr', 'tk', 'ak', 'uk', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu',
}

LANGUAGE_ALIASES = {
    'zh': 'zh-cn',
    'zh-hans': 'zh-cn',
    'zh-hant': 'zh-tw',
    'he': 'iw',
    'fil': 'tl',
    'nb': 'no',
    'nn': 'no',
}


def _format_timestamp(seconds):
    millis = int((seconds % 1) * 1000)
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}.{millis:03}"


def build_vtt(segments):
    lines = ["WEBVTT", ""]
    for segment in segments:
        start = _format_timestamp(float(segment["start"]))
        end = _format_timestamp(float(segment["end"]))
        text = str(segment["text"]).strip()
        if not text:
            continue
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def _resolve_video_path(exercise):
    if exercise.video_file:
        return exercise.video_file.path, None

    if exercise.video_url:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        tmp.close()
        urllib.request.urlretrieve(exercise.video_url, tmp.name)
        return tmp.name, tmp.name

    raise ValueError("У упражнения нет видеофайла или ссылки на видео.")


def _normalize_lang(language):
    return (language or "").strip().lower() or "en"

def _to_translator_code(language, fallback='auto'):
    lang = _normalize_lang(language).replace('_', '-')
    lang = LANGUAGE_ALIASES.get(lang, lang)

    if lang in SUPPORTED_TRANSLATOR_CODES:
        return lang

    short = lang.split('-')[0]
    short = LANGUAGE_ALIASES.get(short, short)
    if short in SUPPORTED_TRANSLATOR_CODES:
        return short

    return fallback

def _translate_segments(segments, source_language, target_language):
    source = _to_translator_code(source_language, fallback='auto')
    target = _to_translator_code(target_language, fallback='en')

    if source == target:
        return segments

    try:
        from deep_translator import GoogleTranslator
    except ImportError as exc:
        raise RuntimeError(
            "Для перевода субтитров установите пакет deep-translator: pip install deep-translator"
        ) from exc

    translator = GoogleTranslator(source=source, target=target)
    translated_segments = []

    for segment in segments:
        text = str(segment.get("text", "")).strip()
        translated_text = translator.translate(text) if text else ""
        translated_segments.append(
            {
                "start": segment["start"],
                "end": segment["end"],
                "text": translated_text,
            }
        )

    return translated_segments

def _build_en_ru_segments(source_segments, source_language):
    source_lang = _normalize_lang(source_language)

    if source_lang == "ru":
        ru_segments = source_segments
        en_segments = _translate_segments(source_segments, source_lang, "en")
    elif source_lang == "en":
        en_segments = source_segments
        ru_segments = _translate_segments(source_segments, source_lang, "ru")
    else:
        en_segments = _translate_segments(source_segments, source_lang, "en")
        ru_segments = _translate_segments(source_segments, source_lang, "ru")

    return en_segments, ru_segments


def generate_offline_subtitles(exercise, model_size="base", generate_ru=True):
    exercise.subtitle_status = "processing"
    exercise.subtitle_error = ""
    exercise.save(update_fields=["subtitle_status", "subtitle_error", "updated_at"])

    temp_path = None
    try:
        video_path, temp_path = _resolve_video_path(exercise)

        try:
            import whisper
        except ImportError as exc:
            raise RuntimeError(
                "Для оффлайн генерации установите пакет openai-whisper и ffmpeg в системе."
            ) from exc

        source_lang = _normalize_lang(exercise.source_language)
        model = whisper.load_model(model_size)
        result = model.transcribe(video_path, language=source_lang, task="transcribe")

        source_segments = result.get("segments") or []
        if not source_segments:
            raise RuntimeError("Whisper не вернул сегменты субтитров.")

        en_segments, ru_segments = _build_en_ru_segments(source_segments, source_lang)

        base_name = exercise.slug or f"exercise_{exercise.id}"
        exercise.subtitle_en_file.save(
            f"{base_name}_en.vtt",
            ContentFile(build_vtt(en_segments).encode("utf-8")),
            save=False,
        )

        if generate_ru:

            exercise.subtitle_ru_file.save(
                f"{base_name}_ru.vtt",
                ContentFile(build_vtt(ru_segments).encode("utf-8")),
                save=False,
            ),

        exercise.subtitle_status = "done"
        exercise.subtitle_error = ""
        update_fields = ["subtitle_en_file", "subtitle_status", "subtitle_error", "updated_at"]
        if generate_ru:
            update_fields.append("subtitle_ru_file")
        exercise.save(update_fields=update_fields)
    except Exception as exc:
        exercise.subtitle_status = "error"
        exercise.subtitle_error = str(exc)
        exercise.save(update_fields=["subtitle_status", "subtitle_error", "updated_at"])
        raise
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)