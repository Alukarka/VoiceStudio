from django.test import TestCase, SimpleTestCase
from django.contrib.messages import get_messages
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from .models import ExerciseCategory, PracticalExercise
from .services.subtitles import build_vtt, _build_en_ru_segments, _to_translator_code


class ExercisesListViewTests(TestCase):
    def setUp(self):
        self.category = ExerciseCategory.objects.create(name='Speech', icon='🎙️')
        self.other_category = ExerciseCategory.objects.create(name='Acting', icon='🎭')

        self.speech_exercise = PracticalExercise.objects.create(
            title='Speech warm up',
            category=self.category,
            description='Desc',
            instruction='Instruction',
            is_active=True,
        )
        PracticalExercise.objects.create(
            title='Acting scene',
            category=self.other_category,
            description='Desc',
            instruction='Instruction',
            is_active=True,
        )

    def test_filters_by_numeric_category_id(self):
        response = self.client.get(reverse('exercises:list'), {'category': str(self.category.id)})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.speech_exercise.title)
        self.assertEqual(len(response.context['exercises']), 1)
        self.assertEqual(response.context['selected_category'], self.category)
        self.assertEqual(response.context['selected_category_id'], self.category.id)

    def test_filters_by_category_name_without_value_error(self):
        response = self.client.get(reverse('exercises:list'), {'category': 'speech'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.speech_exercise.title)
        self.assertEqual(len(response.context['exercises']), 1)
        self.assertEqual(response.context['selected_category'], self.category)
        self.assertEqual(response.context['selected_category_id'], self.category.id)

    def test_categories_have_active_exercises_count(self):
        response = self.client.get(reverse('exercises:list'))

        self.assertEqual(response.status_code, 200)
        categories = list(response.context['categories'])
        category_map = {item.id: item for item in categories}

        self.assertEqual(category_map[self.category.id].active_exercises_count, 1)
        self.assertEqual(category_map[self.other_category.id].active_exercises_count, 1)

    def test_exercises_list_template_compiles(self):
        response = self.client.get(reverse('exercises:list'))

        self.assertEqual(response.status_code, 200)


    def test_detail_always_shows_studio_button(self):
        response = self.client.get(reverse('exercises:detail', args=[self.speech_exercise.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Открыть виртуальную студию')


    def test_unauthorized_user_gets_message_on_record_attempt(self):
        response = self.client.get(reverse('exercises:record', args=[self.speech_exercise.id]), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], reverse('exercises:detail', args=[self.speech_exercise.id]))

        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertIn('Чтобы начать упражнение - Вам нужно авторизоваться', messages)

class StudioViewTests(TestCase):
    def setUp(self):
        self.category = ExerciseCategory.objects.create(name='Speech', icon='🎙️')
        self.exercise = PracticalExercise.objects.create(
            title='Video speech warm up',
            category=self.category,
            description='Desc',
            instruction='Instruction',
            is_active=True,
            video_url='https://example.com/video.mp4',
        )
        self.non_video_exercise = PracticalExercise.objects.create(
            title='No video speech warm up',
            category=self.category,
            description='Desc',
            instruction='Instruction',
            is_active=True,
        )
        self.user = User.objects.create_user(username='tester', password='strong-pass-123')

    def test_studio_requires_authentication_message(self):
        response = self.client.get(reverse('exercises:studio', args=[self.exercise.id]), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], reverse('exercises:detail', args=[self.exercise.id]))
        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertIn('Чтобы начать упражнение - Вам нужно авторизоваться', messages)

    def test_studio_list_shows_only_video_exercises(self):
        response = self.client.get(reverse('exercises:studio_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exercise.title)
        self.assertNotContains(response, self.non_video_exercise.title)

    def test_studio_page_available_for_authenticated_user(self):
        self.client.login(username='tester', password='strong-pass-123')
        response = self.client.get(reverse('exercises:studio', args=[self.exercise.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exercises/studio.html')

class SubtitleUtilsTests(SimpleTestCase):
    def test_build_vtt_renders_valid_header_and_cues(self):
        result = build_vtt([
            {'start': 0.0, 'end': 1.5, 'text': 'Hello world'},
            {'start': 2.0, 'end': 3.2, 'text': 'Second line'},
        ])

        self.assertIn('WEBVTT', result)
        self.assertIn('00:00:00.000 --> 00:00:01.500', result)
        self.assertIn('Hello world', result)
        self.assertIn('00:00:02.000 --> 00:00:03.200', result)

class SubtitleLanguageRoutingTests(SimpleTestCase):
    @patch('exercises.services.subtitles._translate_segments')
    def test_russian_source_keeps_ru_and_translates_en(self, translate_mock):
        source_segments = [{'start': 0.0, 'end': 1.0, 'text': 'Привет'}]
        translate_mock.return_value = [{'start': 0.0, 'end': 1.0, 'text': 'Hello'}]

        en_segments, ru_segments = _build_en_ru_segments(source_segments, 'ru')

        self.assertEqual(ru_segments, source_segments)
        self.assertEqual(en_segments, translate_mock.return_value)
        translate_mock.assert_called_once_with(source_segments, 'ru', 'en')

    @patch('exercises.services.subtitles._translate_segments')
    def test_english_source_keeps_en_and_translates_ru(self, translate_mock):
        source_segments = [{'start': 0.0, 'end': 1.0, 'text': 'Hello'}]
        translate_mock.return_value = [{'start': 0.0, 'end': 1.0, 'text': 'Привет'}]

        en_segments, ru_segments = _build_en_ru_segments(source_segments, 'en')

        self.assertEqual(en_segments, source_segments)
        self.assertEqual(ru_segments, translate_mock.return_value)
        translate_mock.assert_called_once_with(source_segments, 'en', 'ru')

class SubtitleTranslatorCodeTests(SimpleTestCase):
    def test_maps_aliases_and_variants(self):
        self.assertEqual(_to_translator_code('zh'), 'zh-cn')
        self.assertEqual(_to_translator_code('pt-BR'), 'pt')
        self.assertEqual(_to_translator_code('en-US'), 'en')

    def test_unknown_source_falls_back_to_auto(self):
        self.assertEqual(_to_translator_code('xx-unknown'), 'auto')