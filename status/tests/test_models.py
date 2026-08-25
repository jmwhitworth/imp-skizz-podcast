from box_office.tests.factories import EventFactory
from common.test import TestCase
from status.models import StatusModelMixin


class StatusModelMixin__TestCase(TestCase):
    def test_status_choices(self):
        expected_choices = [
            ("DRAFT", "Draft"),
            ("PUBLISHED", "Published"),
            ("ARCHIVED", "Archived"),
        ]
        self.assertEqual(StatusModelMixin.STATUS_CHOICES, expected_choices)

    def test_display_label(self):
        expected_labeling = {
            "DRAFT": "info",
            "PUBLISHED": "success",
            "DEMO": "warning",
        }
        self.assertEqual(StatusModelMixin.DISPLAY_LABEL, expected_labeling)


class TestCase(TestCase):
    def test_model_inherits_from_status_model_mixin(self):
        """
        Uses EventFactory as StatusModelMixin is abstract.
        This test ensures that the other test cases are actually testing the mixin as intended.
        """
        event = EventFactory()
        self.assertTrue(isinstance(event, StatusModelMixin))


class StatusModelMixin__is_draft__TestCase(TestCase):
    def test_returns_true_when_set(self):
        event = EventFactory(status=StatusModelMixin.DRAFT)
        self.assertTrue(event.is_draft)

    def test_returns_false_when_published(self):
        event = EventFactory(status=StatusModelMixin.PUBLISHED)
        self.assertFalse(event.is_draft)

    def test_returns_false_when_archived(self):
        event = EventFactory(status=StatusModelMixin.ARCHIVED)
        self.assertFalse(event.is_draft)

    def test_returns_false_when_unexpected(self):
        cases = ["Foo", ""]
        for case in cases:
            with self.subTest(case=case):
                event = EventFactory(status=case)
                self.assertFalse(event.is_draft)


class StatusModelMixin__is_published__TestCase(TestCase):
    def test_returns_true_when_set(self):
        event = EventFactory(status=StatusModelMixin.PUBLISHED)
        self.assertTrue(event.is_published)

    def test_returns_false_when_draft(self):
        event = EventFactory(status=StatusModelMixin.DRAFT)
        self.assertFalse(event.is_published)

    def test_returns_false_when_archived(self):
        event = EventFactory(status=StatusModelMixin.ARCHIVED)
        self.assertFalse(event.is_published)

    def test_returns_false_when_unexpected(self):
        cases = ["Foo", ""]
        for case in cases:
            with self.subTest(case=case):
                event = EventFactory(status=case)
                self.assertFalse(event.is_published)


class StatusModelMixin__is_archived__TestCase(TestCase):
    def test_returns_true_when_set(self):
        event = EventFactory(status=StatusModelMixin.ARCHIVED)
        self.assertTrue(event.is_archived)

    def test_returns_false_when_draft(self):
        event = EventFactory(status=StatusModelMixin.DRAFT)
        self.assertFalse(event.is_archived)

    def test_returns_false_when_published(self):
        event = EventFactory(status=StatusModelMixin.PUBLISHED)
        self.assertFalse(event.is_archived)

    def test_returns_false_when_unexpected(self):
        cases = ["Foo", ""]
        for case in cases:
            with self.subTest(case=case):
                event = EventFactory(status=case)
                self.assertFalse(event.is_archived)


class StatusModelMixin__is_visible__TestCase(TestCase):
    def test_returns_true_when_published_and_not_demo(self):
        event = EventFactory(status=StatusModelMixin.PUBLISHED)
        self.assertTrue(event.is_visible())

    def test_returns_false_when_draft_and_not_demo(self):
        event = EventFactory(status=StatusModelMixin.DRAFT)
        self.assertFalse(event.is_visible())

    def test_returns_true_when_draft_and_demo(self):
        event = EventFactory(status=StatusModelMixin.DRAFT)
        self.assertTrue(event.is_visible(demo=True))

    def test_returns_true_when_published_and_demo(self):
        event = EventFactory(status=StatusModelMixin.PUBLISHED)
        self.assertTrue(event.is_visible(demo=True))


class StatusModelMixin__status_suffix__TestCase(TestCase):
    def test_returns_expected_when_status_is_draft(self):
        event = EventFactory(status=StatusModelMixin.DRAFT)
        self.assertEqual(event.status_suffix, f" - {StatusModelMixin.DRAFT}")

    def test_returns_expected_when_status_is_archived(self):
        event = EventFactory(status=StatusModelMixin.ARCHIVED)
        self.assertEqual(event.status_suffix, f" - {StatusModelMixin.ARCHIVED}")

    def test_returns_blank_string_when_status_is_published(self):
        event = EventFactory(status=StatusModelMixin.PUBLISHED)
        self.assertEqual(event.status_suffix, "")

    def test_returns_blank_string_when_status_is_unexpected(self):
        cases = ["Foo", ""]
        for case in cases:
            with self.subTest(case=case):
                event = EventFactory(status=case)
                self.assertEqual(event.status_suffix, "")
