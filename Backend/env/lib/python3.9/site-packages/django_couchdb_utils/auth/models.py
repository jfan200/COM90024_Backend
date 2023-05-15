from datetime import datetime
import random

from couchdbkit.ext.django.schema import *
from couchdbkit.exceptions import ResourceNotFound

from django.conf import settings
from django import VERSION as django_version
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password

from django_couchdb_utils.auth import app_label

"""
 django versions < 1.6 backward-compatibly patches
"""

if django_version[:2] > (1, 5):
    # > 1.5.x
    from django.contrib.auth.hashers import is_password_usable

    def get_unusable_password():
        return make_password(None)

else:
    # < 1.6.x
    from django.contrib.auth.models import UNUSABLE_PASSWORD

    def is_password_usable(pwd):
        return pwd != UNUSABLE_PASSWORD

    def get_unusable_password():
        return UNUSABLE_PASSWORD


class SiteProfileNotAvailable(Exception):
    pass


class UsernameException(Exception):
    pass


class PasswordException(Exception):
    pass


class User(Document):
    username      = StringProperty(required=True)
    first_name    = StringProperty(required=False)
    last_name     = StringProperty(required=False)
    email         = StringProperty(required=True)
    password      = StringProperty(required=True)
    is_staff      = BooleanProperty(default=False)
    is_active     = BooleanProperty(default=True)
    is_superuser  = BooleanProperty(default=False)
    last_login    = DateTimeProperty(required=False)
    date_joined   = DateTimeProperty(default=datetime.utcnow)

    class Meta:
        app_label = app_label

    def __unicode__(self):
        return self.username

    def __repr__(self):
        return "<User: %s>" %self.username

    def is_anonymous(self):
        return False

    def save(self, update_fields=[]):
        if not self.check_username():
            raise UsernameException('The username %s is already in use.' % self.username)
        if not self.check_email():
            raise PasswordException('The email address %s is already in use.' % self.email)
        return super(User, self).save()


    def check_username(self):
        u = User.get_user(self.username, is_active=None)
        if u is None:
            return True
        return u._id == self._id

    def check_email(self):
        u = User.get_user_by_email(self.email, is_active=None)
        if u is None:
            return True
        return u._id == self._id

    def _get_id(self):
        return self.username

    id = property(_get_id)
    pk = id

    @property
    def pk(self):
        return self.username

    def get_full_name(self):
        "Returns the first_name plus the last_name, with a space in between."
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def is_authenticated(self):
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        return check_password(raw_password, self.password)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = get_unusable_password()

    def has_usable_password(self):
        return is_password_usable(self.password)

    def email_user(self, subject, message, from_email=None):
        "Sends an e-mail to this User."
        send_mail(subject, message, from_email, [self.email])

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings
            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable('You need to set AUTH_PROFILE_MO'
                                              'DULE in your project settings')
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            except ValueError:
                raise SiteProfileNotAvailable('app_label and model_name should'
                        ' be separated by a dot in the AUTH_PROFILE_MODULE set'
                        'ting')

            try:
                ### model = models.get_model(app_label, model_name)
                from django.db.models.loading import get_app
                app = get_app(app_label)
                model = getattr(app, model_name, None)

                if model is None:
                    raise SiteProfileNotAvailable('Unable to load the profile '
                        'model, check AUTH_PROFILE_MODULE in your project sett'
                        'ings')
                ### self._profile_cache = model._default_manager.using(self._state.db).get(user__id__exact=self.id)
                self._profile_cache = model.get_userprofile(self.get_id)

                ### self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache

    def get_and_delete_messages(self):
        # Todo: Implement messaging and groups.
        return None

    @classmethod
    def get_user(cls, username, is_active=True):
        user = None

        if not user:
            res = cls.view('django_couchdb_utils_auth/users_by_username',
                     include_docs = True,
                     reduce       = False,
                     key          = username,
                )
            user = res.first()

        if user and (not is_active or user.is_active):
            return user

        return None

    @classmethod
    def get_user_by_email(cls, email, is_active=True):
        param = {"key": email}

        r = cls.view('django_couchdb_utils_auth/users_by_email',
                     include_docs=True, **param).first()
        if r and (not is_active or r.is_active):
            return r
        return None

    @classmethod
    def all_users(cls):
        view = cls.view('django_couchdb_utils_auth/users_by_username',
                include_docs=True,
                reduce=False,
            )
        return view.iterator()


    @classmethod
    def count(cls):
        view = cls.view('django_couchdb_utils_auth/users_by_username',
                reduce=True,
            )
        return view.first()['value'] if view else 0


class UserProfile(Document):
    '''This is a dummy class to demonstrate the use of a UserProfile.
    It's used in tests. To use a UserProfile in your app, don't subclass this,
    define your own class, use a permanent view and set AUTH_PROFILE_MODULE in
    settings.py to point to your class.'''
    user_id = StringProperty()
    age = IntegerProperty()

    class Meta:
        app_label = app_label

    @classmethod
    def get_userprofile(cls, user_id):
        # With a permanent view:
        # r = cls.view('%s/userprofile_by_userid' % cls._meta.app_label,
        #              key=user_id, include_docs=True)

        design_doc = {
            "map": """function(doc) { if (doc.doc_type == "UserProfile") { emit(doc.user_id, doc); }}"""
        }
        r = cls.temp_view(design_doc, key=user_id)
        return r.first() if r else None
