import uuid
from unittest.mock import MagicMock, patch

from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from admissions.models import Path
from admissions.models.paths import PathStep
from admissions.tests.factories import PathFactory
from box_office.models import Event
from box_office.tests.factories import EventFactory
from common.test import TestCase
from status.admin import (
    StatusAdminMixin,
    StatusAwareInlineMixin,
    StatusAwareStackedInline,
    StatusAwareTabularInline,
)
from status.models import StatusModelMixin
from status.models import StatusModelMixin as Status
from tenants.admin import SiteAwareStackedInline, SiteAwareTabularInline
from tenants.tests.factories import OrganisationFactory, SiteFactory, UserFactory


class StatusAdminMixin__TestCase(TestCase):
    def setUp(self):
        self.model_admin = StatusAdminMixin(model=Event, admin_site=AdminSite())
        self.client = RequestFactory()
        return super().setUp()

    def _request_with_messages(self):
        """
        RequestFactory bypasses the django messages middleware.
        This helper method creates a request with messages storage attached.
        """
        request = self.client.get("/")
        request.session = {}
        request._messages = FallbackStorage(request)
        return request


class StatusAdminMixin__get_list_display__TestCase(StatusAdminMixin__TestCase):
    def test_returns_expected(self):
        expected = ["show_status"]
        request = self.client.get("/")
        self.assertEqual(self.model_admin.get_list_display(request), expected)


class StatusAdminMixin__get_list_filter__TestCase(StatusAdminMixin__TestCase):
    def test_returns_expected(self):
        request = self.client.get("/")
        filters = self.model_admin.get_list_filter(request)

        # get_list_filters will return a mixed list of tuples and filter classes
        # we just want to test that our 'status' field tuple is included in the filters
        fields = []
        for filter in filters:
            if not filter or not isinstance(filter, tuple):
                continue

            fields.append(filter[0])

        self.assertIn("status", fields)


class StatusAdminMixin__get_queryset__TestCase(StatusAdminMixin__TestCase):
    def test_with_non_autocomplete_request(self):
        EventFactory(status=Status.PUBLISHED)
        EventFactory(status=Status.DRAFT)
        EventFactory(status=Status.ARCHIVED)

        request = self.client.get("/")
        qs = self.model_admin.get_queryset(request)

        self.assertEqual(qs.model, Event)
        self.assertEqual(qs.count(), 3)

    def test_with_autocomplete_request(self):
        EventFactory(status=Status.PUBLISHED)
        EventFactory(status=Status.DRAFT)
        EventFactory(status=Status.ARCHIVED)

        request = self.client.get("/autocomplete/")
        qs = self.model_admin.get_queryset(request)

        self.assertEqual(qs.model, Event)
        self.assertEqual(qs.count(), 2)
        # The queryset should be filtered to non-archived items only
        for event in qs:
            with self.subTest(event=event):
                self.assertNotEqual(event.status, Status.ARCHIVED)


class StatusAdminMixin__show_status__TestCase(StatusAdminMixin__TestCase):
    def test_returns_expected(self):
        cases = (
            StatusModelMixin.DRAFT,
            StatusModelMixin.PUBLISHED,
            StatusModelMixin.ARCHIVED,
        )

        for case in cases:
            with self.subTest(case=case):
                event = EventFactory(status=case)
                self.assertEqual(self.model_admin.show_status(event), case)


class StatusAdminMixin__action_set_published__TestCase(StatusAdminMixin__TestCase):
    def test_with_single_object(self):
        event = EventFactory(status=StatusModelMixin.DRAFT)
        queryset = Event.objects.filter(id=event.id)
        request = self._request_with_messages()

        self.model_admin.action_set_published(
            model_admin=None, request=request, queryset=queryset
        )
        event.refresh_from_db()
        self.assertEqual(event.status, StatusModelMixin.PUBLISHED)
        self.assertEqual(
            request._messages._queued_messages[0].message,
            "1 item was set to published.",
        )

    def test_with_multiple_objects(self):
        events = EventFactory.create_batch(3, status=StatusModelMixin.DRAFT)
        queryset = Event.objects.filter(id__in=[e.id for e in events])
        request = self._request_with_messages()

        self.model_admin.action_set_published(
            model_admin=None, request=request, queryset=queryset
        )
        for event in events:
            event.refresh_from_db()
            self.assertEqual(event.status, StatusModelMixin.PUBLISHED)

        self.assertEqual(
            request._messages._queued_messages[0].message,
            "3 items were set to published.",
        )

    def test_with_no_objects(self):
        queryset = Event.objects.filter(id=uuid.uuid4())  # empty queryset
        request = self._request_with_messages()

        self.model_admin.action_set_published(
            model_admin=None, request=request, queryset=queryset
        )
        self.assertEqual(
            request._messages._queued_messages[0].message,
            "0 items were set to published.",
        )


class StatusAdminMixin__action_set_draft__TestCase(StatusAdminMixin__TestCase):
    def test_with_single_object(self):
        event = EventFactory(status=StatusModelMixin.PUBLISHED)
        queryset = Event.objects.filter(id=event.id)
        request = self._request_with_messages()

        self.model_admin.action_set_draft(
            model_admin=None, request=request, queryset=queryset
        )
        event.refresh_from_db()
        self.assertEqual(event.status, StatusModelMixin.DRAFT)
        self.assertEqual(
            request._messages._queued_messages[0].message,
            "1 item was set to draft.",
        )

    def test_with_multiple_objects(self):
        events = EventFactory.create_batch(3, status=StatusModelMixin.PUBLISHED)
        queryset = Event.objects.filter(id__in=[e.id for e in events])
        request = self._request_with_messages()

        self.model_admin.action_set_draft(
            model_admin=None, request=request, queryset=queryset
        )
        for event in events:
            event.refresh_from_db()
            self.assertEqual(event.status, StatusModelMixin.DRAFT)

        self.assertEqual(
            request._messages._queued_messages[0].message,
            "3 items were set to draft.",
        )

    def test_with_no_items(self):
        queryset = Event.objects.filter(id=uuid.uuid4())  # empty queryset
        request = self._request_with_messages()

        self.model_admin.action_set_draft(
            model_admin=None, request=request, queryset=queryset
        )
        self.assertEqual(
            request._messages._queued_messages[0].message,
            "0 items were set to draft.",
        )


class StatusAdminMixin__action_set_archived__TestCase(StatusAdminMixin__TestCase):
    def test_with_single_item(self):
        event = EventFactory(status=StatusModelMixin.PUBLISHED)
        queryset = Event.objects.filter(id=event.id)
        request = self._request_with_messages()

        self.model_admin.action_set_archived(
            model_admin=None, request=request, queryset=queryset
        )
        event.refresh_from_db()
        self.assertEqual(event.status, StatusModelMixin.ARCHIVED)
        self.assertEqual(
            request._messages._queued_messages[0].message,
            "1 item was set to archived.",
        )

    def test_with_multiple_items(self):
        events = EventFactory.create_batch(3, status=StatusModelMixin.PUBLISHED)
        queryset = Event.objects.filter(id__in=[e.id for e in events])
        request = self._request_with_messages()

        self.model_admin.action_set_archived(
            model_admin=None, request=request, queryset=queryset
        )
        for event in events:
            event.refresh_from_db()
            self.assertEqual(event.status, StatusModelMixin.ARCHIVED)

        self.assertEqual(
            request._messages._queued_messages[0].message,
            "3 items were set to archived.",
        )

    def test_with_no_items(self):
        queryset = Event.objects.filter(id=uuid.uuid4())  # empty queryset
        request = self._request_with_messages()

        self.model_admin.action_set_archived(
            model_admin=None, request=request, queryset=queryset
        )
        self.assertEqual(
            request._messages._queued_messages[0].message,
            "0 items were set to archived.",
        )


class StatusAwareInlineMixin__TestCase:
    """
    Reusable test mixin for any inline that inherits from StatusAwareInlineMixin.
    Subclasses must set:
      inline_class       — the inline class under test
      formfield_patch_path — dotted path to the super formfield_for_foreignkey to patch
    """

    _MISSING = object()

    inline_class = None
    formfield_patch_path = ""

    def _make_request(self, user):
        request = RequestFactory().get("/")
        request.user = user
        return request

    def _call_formfield(self, through_model, field_name, user, site=None, kwargs=None):
        if kwargs is None:
            kwargs = {}
        with patch.object(self.inline_class, "model", through_model):
            inline = self.inline_class(model=through_model, admin_site=AdminSite())
            db_field = MagicMock()
            db_field.name = field_name
            request = self._make_request(user)
            if site is not None:
                request._obj_site = site
            with patch(self.formfield_patch_path) as mock_super:
                inline.formfield_for_foreignkey(db_field, request, **kwargs)
                return mock_super.call_args.kwargs.get("queryset", self._MISSING)

    def test_inline_class_is_subclass_of_status_aware_inline_mixin(self):
        self.assertTrue(issubclass(self.inline_class, StatusAwareInlineMixin))

    def test_published_records_appear_in_queryset_for_mapped_field(self):
        org = OrganisationFactory()
        site = SiteFactory(organisation=org)
        published_path = PathFactory(site=site, status=Status.PUBLISHED)
        user = UserFactory(is_superuser=False, organisation=org)

        queryset = self._call_formfield(PathStep, "path", user, site=site)
        self.assertIn(published_path, queryset)

    def test_draft_records_appear_in_queryset_for_mapped_field(self):
        org = OrganisationFactory()
        site = SiteFactory(organisation=org)
        draft_path = PathFactory(site=site, status=Status.DRAFT)
        user = UserFactory(is_superuser=False, organisation=org)

        queryset = self._call_formfield(PathStep, "path", user, site=site)
        self.assertIn(draft_path, queryset)

    def test_archived_records_excluded_for_mapped_field(self):
        org = OrganisationFactory()
        site = SiteFactory(organisation=org)
        archived_path = PathFactory(site=site, status=Status.ARCHIVED)
        user = UserFactory(is_superuser=False, organisation=org)

        queryset = self._call_formfield(PathStep, "path", user, site=site)
        self.assertNotIn(archived_path, queryset)

    def test_field_not_in_map_is_not_filtered_by_status(self):
        user = UserFactory(is_superuser=False)
        result = self._call_formfield(PathStep, "order", user)
        self.assertIs(result, self._MISSING)


class _CombinedTabularInline(SiteAwareTabularInline, StatusAwareTabularInline):
    """Combined inline used only in tests — provides site_scoped_fields for StatusAwareInlineMixin."""


class _CombinedStackedInline(SiteAwareStackedInline, StatusAwareStackedInline):
    """Combined inline used only in tests — provides site_scoped_fields for StatusAwareInlineMixin."""


class StatusAwareTabularInline__TestCase(StatusAwareInlineMixin__TestCase, TestCase):
    inline_class = _CombinedTabularInline
    formfield_patch_path = "unfold.admin.TabularInline.formfield_for_foreignkey"


class StatusAwareStackedInline__TestCase(StatusAwareInlineMixin__TestCase, TestCase):
    inline_class = _CombinedStackedInline
    formfield_patch_path = "unfold.admin.StackedInline.formfield_for_foreignkey"
