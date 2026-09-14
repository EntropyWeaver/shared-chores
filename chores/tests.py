from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class HomeViewTests(TestCase):
    def test_home_page_renders_successfully(self):
        home_url = reverse('chores:home')

        self.assertEqual(home_url, '/')

        response = self.client.get(home_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shared Chores')
        self.assertTemplateUsed(response, 'chores/home.html')


class AuthenticationFlowTests(TestCase):
    password = 'A-secure-test-password-2026'

    def test_visitor_can_create_account_and_is_logged_in(self):
        response = self.client.post(
            reverse('chores:signup'),
            {
                'username': 'borja',
                'password1': self.password,
                'password2': self.password,
            },
        )

        self.assertRedirects(response, reverse('chores:dashboard'))
        self.assertTrue(User.objects.filter(username='borja').exists())
        self.assertEqual(self.client.session['_auth_user_id'], str(User.objects.get().pk))

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(username='borja', password=self.password)

        response = self.client.post(
            reverse('chores:signup'),
            {
                'username': 'borja',
                'password1': self.password,
                'password2': self.password,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.context['form'].errors)
        self.assertEqual(User.objects.filter(username='borja').count(), 1)

    def test_registered_user_can_log_in_and_log_out(self):
        User.objects.create_user(username='borja', password=self.password)

        login_response = self.client.post(
            reverse('chores:login'),
            {'username': 'borja', 'password': self.password},
        )

        self.assertRedirects(login_response, reverse('chores:dashboard'))
        self.assertEqual(self.client.get(reverse('chores:dashboard')).status_code, 200)

        logout_response = self.client.post(reverse('chores:logout'))

        self.assertRedirects(logout_response, reverse('chores:home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_private_route_redirects_anonymous_visitor_to_login(self):
        response = self.client.get(reverse('chores:dashboard'))

        expected_url = f"{reverse('chores:login')}?next={reverse('chores:dashboard')}"
        self.assertRedirects(response, expected_url)

    def test_logout_rejects_get_requests(self):
        User.objects.create_user(username='borja', password=self.password)
        self.client.login(username='borja', password=self.password)

        response = self.client.get(reverse('chores:logout'))

        self.assertEqual(response.status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)
