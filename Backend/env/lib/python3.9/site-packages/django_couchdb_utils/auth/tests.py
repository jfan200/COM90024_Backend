from django.contrib.auth import authenticate
from django.conf import settings

from django_couchdb_utils.auth import app_label
from django_couchdb_utils.test.utils import DbTester
from django_couchdb_utils.auth.models import User, UserProfile

class AuthTests(DbTester):
    def setUp(self):
        super(self.__class__, self).setUp(app_label)

    def test_user_registration(self):
        data = {
            'username': 'frank-1',
            'password': 'secret',
            'email': 'user@host.com',
        }
        user = User(**data)
        user.save()

        user = User.get_user(data['username'])
        self.assertIsNotNone(user)
        self.assertEqual(user.username, data['username'])

        user = User.get_user_by_email(data['email'])
        self.assertIsNotNone(user)
        self.assertEqual(user.username, data['username'])

    def test_username_uniqueness(self):
        data = {
            'username': 'frank-2',
            'password': 'secret',
            'email': 'user@host.com',
        }
        user = User(**data)
        user.save()

        user2 = User(**data)
        self.assertExcMsg(Exception, 'The username %s is already in use.' % data.get('username'),
                          user2.save)

    def test_email_uniqueness(self):
        data = {
            'username': 'frank-3',
            'password': 'secret',
            'email': 'user@host.com',
        }
        user = User(**data)
        user.save()

        data.update({
            'username': 'mark',
        })
        user2 = User(**data)
        self.assertExcMsg(Exception, 'The email address %s is already in use.' % data.get('email'),
                          user2.save)

    def test_user_change_email(self):
        data = {
            'username': 'frank-4',
            'password': 'secret',
            'email': 'user@host.com',
        }
        user = User(**data)
        user.save()

        user = User.get_user_by_email(data['email'])
        user.email = 'notme@otherhost.com'
        user.save()

    def test_user_authentication(self):
        authdata = {
            'username': 'mickey',
            'password': 'secret',
            'email': 'user@host.com',
        }
        data = authdata.copy()
        data.update({
            'email': 'mickey@mice.com',
        })
        user = User(**data)
        user.set_password(data.get('password'))
        user.save()

        user = authenticate(username=authdata.get('username'), password=authdata.get('password'))
        self.assertIsNotNone(user)

    def test_user_profile(self):
        settings.AUTH_PROFILE_MODULE = 'auth.UserProfile'

        data = {
            'username': 'frank-5',
            'password': 'secret',
            'email': 'user@host.com',
        }
        user = User(**data)
        user.save()

        profiledata = {
            'user_id': user.get_id,
            'age': 7,
        }
        userprofile = UserProfile(**profiledata)
        userprofile.save()

        userprofile = UserProfile.get_userprofile(profiledata['user_id'])
        self.assertIsNotNone(userprofile)

        self.assertEqual(user.get_profile().age, profiledata['age'])


### XXX older doctest code

BASIC_TESTS = """
>>> from django_couchdb_utils.auth.models import User
>>> from django.contrib.auth.models import UNUSABLE_PASSWORD
>>> u = User(username='testuser', email='test@example.com', password='testpw')
>>> u.set_password('testpw')
>>> u.save()
>>> u.has_usable_password()
True
>>> u.check_password('bad')
False
>>> u.check_password('testpw')
True
>>> u.set_unusable_password()
>>> u.has_usable_password()
False
>>> u2 = User(username='testuser2', email='test2@example.com')
>>> u2.password = UNUSABLE_PASSWORD
>>> u2.save()
>>> u2.has_usable_password()
False

>>> u.is_authenticated()
True
>>> u.is_staff
False
>>> u.is_active
True
>>> u.is_superuser
False
"""

__test__ = {
    'BASIC_TESTS': BASIC_TESTS,
}


if __name__ == '__main__':
    import doctest
    doctest.testmod()
