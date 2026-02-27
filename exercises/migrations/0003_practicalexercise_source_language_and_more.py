from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0002_practicalexercise_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='practicalexercise',
            name='source_language',
            field=models.CharField(default='en', max_length=10, verbose_name='Язык оригинала'),
        ),
        migrations.AddField(
            model_name='practicalexercise',
            name='subtitle_en_file',
            field=models.FileField(blank=True, null=True, upload_to='exercises/subtitles/', verbose_name='Английские субтитры (VTT)'),
        ),
        migrations.AddField(
            model_name='practicalexercise',
            name='subtitle_error',
            field=models.TextField(blank=True, verbose_name='Описание ошибки субтитров'),
        ),
        migrations.AddField(
            model_name='practicalexercise',
            name='subtitle_ru_file',
            field=models.FileField(blank=True, null=True, upload_to='exercises/subtitles/', verbose_name='Русские субтитры (VTT)'),
        ),
        migrations.AddField(
            model_name='practicalexercise',
            name='subtitle_status',
            field=models.CharField(choices=[('none', 'Не загружены'), ('pending', 'В очереди'), ('processing', 'Обрабатываются'), ('done', 'Готово'), ('error', 'Ошибка')], default='none', max_length=20, verbose_name='Статус субтитров'),
        ),
        migrations.AddField(
            model_name='practicalexercise',
            name='video_file',
            field=models.FileField(blank=True, null=True, upload_to='exercises/videos/', verbose_name='Видео для тренировки'),
        ),
        migrations.AddField(
            model_name='practicalexercise',
            name='video_url',
            field=models.URLField(blank=True, verbose_name='Ссылка на видео'),
        ),
    ]