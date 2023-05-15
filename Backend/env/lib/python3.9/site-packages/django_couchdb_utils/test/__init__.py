"""
To run tests against couchdb you need to set TEST_RUNNER in settings.py:
TEST_RUNNER = 'couchdbkit.ext.django.testrunner.CouchDbKitTestSuiteRunner'

This will dispatch the right thing to the right place, it will run the tests
against a temporary <dbname>_test database.

Django's config checks will still run, so make sure the DATABASES setting can
pass scrutiny, otherwise it errors out:

DATABASES = {
    'default': {
        'ENGINE': 'sqlite3',
        'NAME': 'throwaway.db',
    }
}

Then execute the test runner in the standard way:
$ python manage.py test django_couchdb_utils
"""
