from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .forms import CreationForm

User = get_user_model()


class PostURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exists(self):
        templates = [
            "/auth/signup/",
            "/auth/login/",
            "/auth/logout/",
            "/auth/password_change/done/",
            "/auth/password_reset/",
            "/auth/password_reset/done/",
            "/auth/reset/done/",
        ]
        for adress in templates:
            with self.subTest(adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "/auth/signup/": "users/signup.html",
            "/auth/login/": "users/login.html",
            "/auth/logout/": "users/logged_out.html",
            "/auth/password_change/done/": "users/password_change_done.html",
            "/auth/password_reset/": "users/password_reset_form.html",
            "/auth/password_reset/done/": "users/password_reset_done.html",
            "/auth/reset/done/": "users/password_reset_complete.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)


class UsersViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        response = self.guest_client.get(reverse("users:signup"))
        self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        response = self.guest_client.get(reverse("users:signup"))
        self.assertTemplateUsed(response, "users/signup.html")


class CreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create()
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()

    def test_signup(self):
        users_count = User.objects.count()
        form_data = {
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "username": "test_name",
            "email": "email_test@mail.ru",
            "password1": "Django_2022",
            "password2": "Django_2022",
        }
        self.guest_client.post(
            reverse("users:signup"), data=form_data
        )
        self.assertEqual(User.objects.count(), users_count + 1)
