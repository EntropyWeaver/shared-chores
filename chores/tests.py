from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from chores.models import Household, Membership


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


class HouseholdModelTests(TestCase):
    def test_household_has_name_and_unique_access_code(self):
        household = Household.objects.create(
            name='Piso de Salamanca',
            access_code='SALAMANCA1',
        )

        self.assertEqual(str(household), 'Piso de Salamanca')
        self.assertEqual(household.access_code, 'SALAMANCA1')

        with self.assertRaises(IntegrityError), transaction.atomic():
            Household.objects.create(
                name='Otro piso',
                access_code='SALAMANCA1',
            )

    def test_user_can_belong_to_only_one_household(self):
        user = User.objects.create_user(username='borja')
        first_household = Household.objects.create(
            name='Primer piso',
            access_code='FIRST',
        )
        second_household = Household.objects.create(
            name='Segundo piso',
            access_code='SECOND',
        )
        first_household.add_member(user)

        with self.assertRaises(ValidationError):
            second_household.add_member(user)

        self.assertEqual(Membership.objects.filter(user=user).count(), 1)
        self.assertEqual(user.membership.household, first_household)

    def test_household_accepts_at_most_six_members(self):
        household = Household.objects.create(
            name='Piso completo',
            access_code='FULLHOUSE',
        )
        users = [
            User.objects.create_user(username=f'roommate-{number}')
            for number in range(1, 8)
        ]

        for user in users[:6]:
            household.add_member(user)

        with self.assertRaises(ValidationError):
            household.add_member(users[6])

        self.assertEqual(household.member_count, 6)
        self.assertTrue(household.is_full)
        self.assertFalse(Membership.objects.filter(user=users[6]).exists())


class HouseholdFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='borja')
        self.client.force_login(self.user)

    def test_household_routes_require_authentication(self):
        self.client.logout()

        for route_name in ('create-household', 'join-household'):
            with self.subTest(route_name=route_name):
                route = reverse(f'chores:{route_name}')
                response = self.client.get(route)

                self.assertRedirects(
                    response,
                    f"{reverse('chores:login')}?next={route}",
                )

    @patch('chores.services.generate_access_code', return_value='ROOM2026')
    def test_user_can_create_household_and_becomes_first_member(self, _code):
        response = self.client.post(
            reverse('chores:create-household'),
            {'name': 'Piso de Salamanca'},
            follow=True,
        )

        household = Household.objects.get()
        self.assertRedirects(response, reverse('chores:dashboard'))
        self.assertEqual(household.name, 'Piso de Salamanca')
        self.assertEqual(household.access_code, 'ROOM2026')
        self.assertEqual(self.user.membership.household, household)
        self.assertEqual(household.member_count, 1)
        self.assertContains(response, 'ROOM2026')

    def test_user_can_join_household_with_normalized_valid_code(self):
        household = Household.objects.create(
            name='Piso compartido',
            access_code='JOIN2026',
        )

        response = self.client.post(
            reverse('chores:join-household'),
            {'access_code': '  join2026  '},
            follow=True,
        )

        self.assertRedirects(response, reverse('chores:dashboard'))
        self.assertEqual(self.user.membership.household, household)
        self.assertEqual(household.member_count, 1)
        self.assertContains(response, 'Piso compartido')
        self.assertContains(response, 'JOIN2026')

    def test_unknown_code_shows_error_without_changing_data(self):
        response = self.client.post(
            reverse('chores:join-household'),
            {'access_code': 'UNKNOWN'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No existe ningún hogar con ese código.')
        self.assertFalse(Membership.objects.filter(user=self.user).exists())
        self.assertEqual(Household.objects.count(), 0)

    def test_full_household_shows_error_without_adding_user(self):
        household = Household.objects.create(
            name='Piso completo',
            access_code='FULL2026',
        )
        for number in range(6):
            household.add_member(
                User.objects.create_user(username=f'member-{number}')
            )

        response = self.client.post(
            reverse('chores:join-household'),
            {'access_code': 'FULL2026'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ese hogar ya tiene 6 miembros.')
        self.assertEqual(household.member_count, 6)
        self.assertFalse(Membership.objects.filter(user=self.user).exists())

    def test_existing_member_cannot_create_or_join_another_household(self):
        current_household = Household.objects.create(
            name='Mi piso',
            access_code='CURRENT1',
        )
        target_household = Household.objects.create(
            name='Otro piso',
            access_code='TARGET01',
        )
        current_household.add_member(self.user)

        create_response = self.client.post(
            reverse('chores:create-household'),
            {'name': 'Tercer piso'},
            follow=True,
        )
        join_response = self.client.post(
            reverse('chores:join-household'),
            {'access_code': target_household.access_code},
            follow=True,
        )

        self.assertContains(create_response, 'Ya perteneces a un hogar.')
        self.assertContains(join_response, 'Ya perteneces a un hogar.')
        self.assertEqual(Household.objects.count(), 2)
        self.assertEqual(Membership.objects.filter(user=self.user).count(), 1)
        self.assertEqual(self.user.membership.household, current_household)

    @patch(
        'chores.services.generate_access_code',
        side_effect=('TAKEN123', 'FRESH123'),
    )
    def test_code_generation_retries_after_a_collision(self, _code):
        Household.objects.create(name='Existente', access_code='TAKEN123')

        response = self.client.post(
            reverse('chores:create-household'),
            {'name': 'Nuevo piso'},
        )

        self.assertRedirects(response, reverse('chores:dashboard'))
        self.assertTrue(
            Household.objects.filter(
                name='Nuevo piso',
                access_code='FRESH123',
            ).exists()
        )
