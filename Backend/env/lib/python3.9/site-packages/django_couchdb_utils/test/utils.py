from django.test import TestCase

from couchdbkit.ext.django.loading import get_db


class AssertMixin(TestCase):
    def assertExcMsg(self, exc, msg, callable, *args, **kw):
        '''
        Workaround for assertRaisesRegexp, which seems to be broken in stdlib. In
        theory the instructed use is:

        with self.assertRaisesRegexp(ValueError, 'literal'):
           int('XYZ')
       '''

        with self.assertRaises(exc) as cm:
            callable(*args, **kw)
        self.assertEqual(str(cm.exception), msg)

class DbTester(AssertMixin):
    '''Keep separate from TestHelper to make it subclassable as library code'''
    def setUp(self, app_label):
        db = get_db(app_label)
        db.flush()
