from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):
    def test_home_page_renders_successfully(self):
        home_url = reverse('chores:home')

        self.assertEqual(home_url, '/')

        response = self.client.get(home_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shared Chores')
        self.assertTemplateUsed(response, 'chores/home.html')
