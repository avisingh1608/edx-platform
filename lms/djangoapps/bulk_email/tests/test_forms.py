# -*- coding: utf-8 -*-
"""
Unit tests for bulk-email-related forms.
"""
from django.conf import settings
from django.test.utils import override_settings
from mock import patch

from bulk_email.models import CourseAuthorization, CourseEmailTemplate
from bulk_email.forms import CourseAuthorizationAdminForm, CourseEmailTemplateForm
from xmodule.modulestore.tests.django_utils import (
    TEST_DATA_MOCK_MODULESTORE, TEST_DATA_MIXED_TOY_MODULESTORE
)
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.django import modulestore
from xmodule.modulestore import ModuleStoreEnum


class CourseAuthorizationFormTest(ModuleStoreTestCase):
    """Test the CourseAuthorizationAdminForm form for Mongo-backed courses."""

    def setUp(self):
        super(CourseAuthorizationFormTest, self).setUp()
        course_title = u"ẗëṡẗ title ｲ乇丂ｲ ﾶ乇丂丂ﾑg乇 ｷo尺 ﾑﾚﾚ тэѕт мэѕѕаБэ"
        self.course = CourseFactory.create(display_name=course_title)

    def tearDown(self):
        """
        Undo all patches.
        """
        patch.stopall()

    @patch.dict(settings.FEATURES, {'ENABLE_INSTRUCTOR_EMAIL': True, 'REQUIRE_COURSE_EMAIL_AUTH': True})
    def test_authorize_mongo_course(self):
        # Initially course shouldn't be authorized
        self.assertFalse(CourseAuthorization.instructor_email_enabled(self.course.id))
        # Test authorizing the course, which should totally work
        form_data = {'course_id': self.course.id.to_deprecated_string(), 'email_enabled': True}
        form = CourseAuthorizationAdminForm(data=form_data)
        # Validation should work
        self.assertTrue(form.is_valid())
        form.save()
        # Check that this course is authorized
        self.assertTrue(CourseAuthorization.instructor_email_enabled(self.course.id))

    @patch.dict(settings.FEATURES, {'ENABLE_INSTRUCTOR_EMAIL': True, 'REQUIRE_COURSE_EMAIL_AUTH': True})
    def test_repeat_course(self):
        # Initially course shouldn't be authorized
        self.assertFalse(CourseAuthorization.instructor_email_enabled(self.course.id))
        # Test authorizing the course, which should totally work
        form_data = {'course_id': self.course.id.to_deprecated_string(), 'email_enabled': True}
        form = CourseAuthorizationAdminForm(data=form_data)
        # Validation should work
        self.assertTrue(form.is_valid())
        form.save()
        # Check that this course is authorized
        self.assertTrue(CourseAuthorization.instructor_email_enabled(self.course.id))

        # Now make a new course authorization with the same course id that tries to turn email off
        form_data = {'course_id': self.course.id.to_deprecated_string(), 'email_enabled': False}
        form = CourseAuthorizationAdminForm(data=form_data)
        # Validation should not work because course_id field is unique
        self.assertFalse(form.is_valid())
        self.assertEquals(
            "Course authorization with this Course id already exists.",
            form._errors['course_id'][0]  # pylint: disable=protected-access
        )
        with self.assertRaisesRegexp(ValueError, "The CourseAuthorization could not be created because the data didn't validate."):
            form.save()

        # Course should still be authorized (invalid attempt had no effect)
        self.assertTrue(CourseAuthorization.instructor_email_enabled(self.course.id))

    @patch.dict(settings.FEATURES, {'ENABLE_INSTRUCTOR_EMAIL': True, 'REQUIRE_COURSE_EMAIL_AUTH': True})
    def test_form_typo(self):
        # Munge course id
        bad_id = SlashSeparatedCourseKey(u'Broken{}'.format(self.course.id.org), 'hello', self.course.id.run + '_typo')

        form_data = {'course_id': bad_id.to_deprecated_string(), 'email_enabled': True}
        form = CourseAuthorizationAdminForm(data=form_data)
        # Validation shouldn't work
        self.assertFalse(form.is_valid())

        msg = u'COURSE NOT FOUND'
        msg += u' --- Entered course id was: "{0}". '.format(bad_id.to_deprecated_string())
        msg += 'Please recheck that you have supplied a valid course id.'
        self.assertEquals(msg, form._errors['course_id'][0])  # pylint: disable=protected-access

        with self.assertRaisesRegexp(ValueError, "The CourseAuthorization could not be created because the data didn't validate."):
            form.save()

    @patch.dict(settings.FEATURES, {'ENABLE_INSTRUCTOR_EMAIL': True, 'REQUIRE_COURSE_EMAIL_AUTH': True})
    def test_form_invalid_key(self):
        form_data = {'course_id': "asd::**!@#$%^&*())//foobar!!", 'email_enabled': True}
        form = CourseAuthorizationAdminForm(data=form_data)
        # Validation shouldn't work
        self.assertFalse(form.is_valid())

        msg = u'Course id invalid.'
        msg += u' --- Entered course id was: "asd::**!@#$%^&*())//foobar!!". '
        msg += 'Please recheck that you have supplied a valid course id.'
        self.assertEquals(msg, form._errors['course_id'][0])  # pylint: disable=protected-access

        with self.assertRaisesRegexp(ValueError, "The CourseAuthorization could not be created because the data didn't validate."):
            form.save()

    @patch.dict(settings.FEATURES, {'ENABLE_INSTRUCTOR_EMAIL': True, 'REQUIRE_COURSE_EMAIL_AUTH': True})
    def test_course_name_only(self):
        # Munge course id - common
        form_data = {'course_id': self.course.id.run, 'email_enabled': True}
        form = CourseAuthorizationAdminForm(data=form_data)
        # Validation shouldn't work
        self.assertFalse(form.is_valid())

        error_msg = form._errors['course_id'][0]
        self.assertIn(u'--- Entered course id was: "{0}". '.format(self.course.id.run), error_msg)
        self.assertIn(u'Please recheck that you have supplied a valid course id.', error_msg)

        with self.assertRaisesRegexp(ValueError, "The CourseAuthorization could not be created because the data didn't validate."):
            form.save()


class CourseAuthorizationXMLFormTest(ModuleStoreTestCase):
    """Check that XML courses cannot be authorized for email."""
    MODULESTORE = TEST_DATA_MIXED_TOY_MODULESTORE

    @patch.dict(settings.FEATURES, {'ENABLE_INSTRUCTOR_EMAIL': True, 'REQUIRE_COURSE_EMAIL_AUTH': True})
    def test_xml_course_authorization(self):
        course_id = SlashSeparatedCourseKey('edX', 'toy', '2012_Fall')
        # Assert this is an XML course
        self.assertEqual(modulestore().get_modulestore_type(course_id), ModuleStoreEnum.Type.xml)

        form_data = {'course_id': course_id.to_deprecated_string(), 'email_enabled': True}
        form = CourseAuthorizationAdminForm(data=form_data)
        # Validation shouldn't work
        self.assertFalse(form.is_valid())

        msg = u"Course Email feature is only available for courses authored in Studio. "
        msg += u'"{0}" appears to be an XML backed course.'.format(course_id.to_deprecated_string())
        self.assertEquals(msg, form._errors['course_id'][0])  # pylint: disable=protected-access

        with self.assertRaisesRegexp(ValueError, "The CourseAuthorization could not be created because the data didn't validate."):
            form.save()


class CourseEmailTemplateFormTest(ModuleStoreTestCase):
    """Test the CourseEmailTemplateForm that is used in the Django admin subsystem."""

    def test_missing_message_body_in_html(self):
        """
        Asserts that we fail validation if we do not have the {{message_body}} tag
        in the submitted HTML template
        """
        form_data = {
            'html_template': '',
            'plain_template': '{{message_body}}',
            'name': ''
        }
        form = CourseEmailTemplateForm(form_data)
        self.assertFalse(form.is_valid())

    def test_missing_message_body_in_plain(self):
        """
        Asserts that we fail validation if we do not have the {{message_body}} tag
        in the submitted plain template
        """
        form_data = {
            'html_template': '{{message_body}}',
            'plain_template': '',
            'name': ''
        }
        form = CourseEmailTemplateForm(form_data)
        self.assertFalse(form.is_valid())

    def test_blank_name_is_null(self):
        """
        Asserts that submitting a CourseEmailTemplateForm with a blank name is stored
        as a NULL in the database
        """
        form_data = {
            'html_template': '{{message_body}}',
            'plain_template': '{{message_body}}',
            'name': ''
        }
        form = CourseEmailTemplateForm(form_data)
        self.assertTrue(form.is_valid())
        form.save()

        # now inspect the database and make sure the blank name was stored as a NULL
        # Note this will throw an exception if it is not found
        cet = CourseEmailTemplate.objects.get(name=None)
        self.assertIsNotNone(cet)

    def test_name_with_only_spaces_is_null(self):
        """
        Asserts that submitting a CourseEmailTemplateForm just blank whitespace is stored
        as a NULL in the database
        """
        form_data = {
            'html_template': '{{message_body}}',
            'plain_template': '{{message_body}}',
            'name': '   '
        }
        form = CourseEmailTemplateForm(form_data)
        self.assertTrue(form.is_valid())
        form.save()

        # now inspect the database and make sure the whitespace only name was stored as a NULL
        # Note this will throw an exception if it is not found
        cet = CourseEmailTemplate.objects.get(name=None)
        self.assertIsNotNone(cet)

    def test_name_with_spaces_is_trimmed(self):
        """
        Asserts that submitting a CourseEmailTemplateForm with a name that contains
        whitespace at the beginning or end of a name is stripped
        """
        form_data = {
            'html_template': '{{message_body}}',
            'plain_template': '{{message_body}}',
            'name': ' foo  '
        }
        form = CourseEmailTemplateForm(form_data)
        self.assertTrue(form.is_valid())
        form.save()

        # now inspect the database and make sure the name is properly
        # stripped
        cet = CourseEmailTemplate.objects.get(name='foo')
        self.assertIsNotNone(cet)

    def test_non_blank_name(self):
        """
        Asserts that submitting a CourseEmailTemplateForm with a non-blank name
        can be found in the database under than name as a look-up key
        """
        form_data = {
            'html_template': '{{message_body}}',
            'plain_template': '{{message_body}}',
            'name': 'foo'
        }
        form = CourseEmailTemplateForm(form_data)
        self.assertTrue(form.is_valid())
        form.save()

        # now inspect the database and make sure the blank name was stored as a NULL
        # Note this will throw an exception if it is not found
        cet = CourseEmailTemplate.objects.get(name='foo')
        self.assertIsNotNone(cet)

    def test_duplicate_name(self):
        """
        Assert that we cannot submit a CourseEmailTemplateForm with a name
        that already exists
        """

        # first set up one template
        form_data = {
            'html_template': '{{message_body}}',
            'plain_template': '{{message_body}}',
            'name': 'foo'
        }
        form = CourseEmailTemplateForm(form_data)
        self.assertTrue(form.is_valid())
        form.save()

        # try to submit form with the same name
        form = CourseEmailTemplateForm(form_data)
        self.assertFalse(form.is_valid())

        # try again with a name with extra whitespace
        # this should fail as we strip the whitespace away
        form_data = {
            'html_template': '{{message_body}}',
            'plain_template': '{{message_body}}',
            'name': '  foo '
        }
        form = CourseEmailTemplateForm(form_data)
        self.assertFalse(form.is_valid())

        # then try a different name
        form_data = {
            'html_template': '{{message_body}}',
            'plain_template': '{{message_body}}',
            'name': 'bar'
        }
        form = CourseEmailTemplateForm(form_data)
        self.assertTrue(form.is_valid())
        form.save()

        form = CourseEmailTemplateForm(form_data)
        self.assertFalse(form.is_valid())
