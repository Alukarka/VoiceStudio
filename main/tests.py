from django.test import TestCase
from django.urls import reverse

# Create your tests here.

class MainPagesTests(TestCase):
    def test_contacts_page_available(self):
        response = self.client.get(reverse('contacts'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Контакты VoiceStudio')

    def test_contacts_link_visible_in_navigation(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/contacts/"')
