from django.test import TestCase

from accounts.models import User


class UserRoleTests(TestCase):
    def test_default_role_is_staff(self):
        user = User.objects.create_user(username="utilisateur", password="Test12345!")

        self.assertEqual(user.role, User.Role.STAFF)

    def test_can_assign_role(self):
        user = User.objects.create_user(
            username="manager",
            password="Test12345!",
            role=User.Role.MANAGER,
        )

        self.assertEqual(user.role, User.Role.MANAGER)
