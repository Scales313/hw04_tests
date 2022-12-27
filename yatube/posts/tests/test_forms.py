from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="NoName")
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        self.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.id
        }
        self.authorized_client.post(
            reverse("posts:post_create"), data=form_data
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text="Тестовый текст",
            group_id=self.group.id,
            author=self.user
        ).exists())

    def test_post_edit(self):
        self.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        self.post = Post.objects.create(
            author=self.user,
            text="Тестовый текст",
            group=self.group
        )
        posts_count = Post.objects.count()
        form_data = {"text": "Измененный текст", "group": self.group.id}
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=({self.post.id})),
            data=form_data,
        )
        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={
                "post_id": self.post.id
            })
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(text="Измененный текст").exists())
