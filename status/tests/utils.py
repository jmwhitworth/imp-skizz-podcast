from status.models import StatusModelMixin


class StatusQuerySetTestMixin:
    model_factory = None
    model_class = None

    def test_uses_status_queryset(self):
        self.model_factory(status=StatusModelMixin.ARCHIVED)
        self.model_factory.create_batch(2, status=StatusModelMixin.PUBLISHED)
        self.model_factory.create_batch(3, status=StatusModelMixin.DRAFT)

        archived = self.model_class.objects.archived()
        self.assertEqual(archived.count(), 1)
        self.assertTrue(all(e.status == StatusModelMixin.ARCHIVED for e in archived))

        not_archived = self.model_class.objects.not_archived()
        self.assertEqual(not_archived.count(), 5)
        self.assertTrue(
            all(e.status != StatusModelMixin.ARCHIVED for e in not_archived)
        )

        published = self.model_class.objects.published()
        self.assertEqual(published.count(), 2)
        self.assertTrue(all(e.status == StatusModelMixin.PUBLISHED for e in published))

        not_published = self.model_class.objects.not_published()
        self.assertEqual(not_published.count(), 4)
        self.assertTrue(
            all(e.status != StatusModelMixin.PUBLISHED for e in not_published)
        )

        draft = self.model_class.objects.draft()
        self.assertEqual(draft.count(), 3)
        self.assertTrue(all(e.status == StatusModelMixin.DRAFT for e in draft))

        not_draft = self.model_class.objects.not_draft()
        self.assertEqual(not_draft.count(), 3)
        self.assertTrue(all(e.status != StatusModelMixin.DRAFT for e in not_draft))
