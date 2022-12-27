from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from yatube.settings import POSTS_ON_PAGE

from ..models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="User")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )
        cls.templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": cls.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": cls.post.author}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": cls.post.id}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": cls.post.id}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def test_pages_uses_correct_template(self):
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        response = self.guest_client.get(reverse("posts:index"))
        expected = list(Post.objects.all()[:POSTS_ON_PAGE])
        self.assertEqual(list(response.context["page_obj"]), expected)

    def test_group_list_show_correct_context(self):
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        expected = list(Post.objects.filter(
            group_id=self.group.id)[:POSTS_ON_PAGE]
        )
        expected2 = response.context['group']
        self.assertEqual(list(response.context["page_obj"]), expected)
        self.assertEqual(self.group, expected2)

    def test_profile_show_correct_context(self):
        response = self.guest_client.get(
            reverse("posts:profile", args=(self.post.author,))
        )
        expected = list(Post.objects.filter(
            author_id=self.user.id)[:POSTS_ON_PAGE]
        )
        expected2 = response.context['author']
        self.assertEqual(self.user, expected2)
        self.assertEqual(list(response.context["page_obj"]), expected)

    def test_post_detail_show_correct_context(self):
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.context.get("post").text, self.post.text)
        self.assertEqual(response.context.get("post").author, self.post.author)
        self.assertEqual(response.context.get("post").group, self.post.group)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for template, expected in form_fields.items():
            with self.subTest(template=template):
                form_field = response.context["form"].fields[template]
                self.assertIsInstance(form_field, expected)

    def test_create_show_correct_context(self):
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for template, expected in form_fields.items():
            with self.subTest(template=template):
                form_field = response.context["form"].fields[template]
                self.assertIsInstance(form_field, expected)

    def test_check_group_not_in_mistake_group_list_page(self):
        response = self.authorized_client.get(reverse(
            "posts:group_list", kwargs={"slug": self.group.slug}
        ))
        form_field = response.context["page_obj"]
        expected = Post.objects.exclude(group=self.post.group)
        self.assertNotIn(expected, form_field)

    def test_paginator_correct_context(self):
        paginator_objects = []
        for i in range(1, 13):
            new_post = Post(
                author=self.user,
                text='Тестовый пост ' + str(i),
                group=self.group
            )
            paginator_objects.append(new_post)
        Post.objects.bulk_create(paginator_objects)
        paginator_data = {
            'index': reverse('posts:index'),
            'group': reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        }
        for paginator_place, paginator_page in paginator_data.items():
            with self.subTest(paginator_place=paginator_place):
                page_1 = self.authorized_client.get(paginator_page)
                page_2 = self.authorized_client.get(
                    paginator_page + '?page=2'
                )
                self.assertEqual(len(
                    page_1.context['page_obj']),
                    10
                )
                self.assertEqual(len(
                    page_2.context['page_obj']),
                    3
                )
