from django.db import models
from django.utils.translation import gettext_lazy as _


class StatusQuerySet(models.QuerySet):
    """Custom queryset to filter records based on their status."""

    def published(self):
        """Return only records with status 'PUBLISHED'."""
        return self.filter(status=StatusModelMixin.PUBLISHED)

    def not_published(self):
        """Return only records with status not 'PUBLISHED'."""
        return self.exclude(status=StatusModelMixin.PUBLISHED)

    def draft(self):
        """Return only records with status 'DRAFT'."""
        return self.filter(status=StatusModelMixin.DRAFT)

    def not_draft(self):
        """Return only records with status not 'DRAFT'."""
        return self.exclude(status=StatusModelMixin.DRAFT)

    def archived(self):
        """Return only records with status 'ARCHIVED'."""
        return self.filter(status=StatusModelMixin.ARCHIVED)

    def not_archived(self):
        """Return only records with status not 'ARCHIVED'."""
        return self.exclude(status=StatusModelMixin.ARCHIVED)


class StatusModelMixin(models.Model):
    """
    Mixin to add status functionality to models.
    This is a placeholder for any common fields or methods related to status management.
    """

    objects = StatusQuerySet.as_manager()

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"

    STATUS_CHOICES = [
        (DRAFT, _("Draft")),
        (PUBLISHED, _("Published")),
        (ARCHIVED, _("Archived")),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT",
        verbose_name=_("Status"),
    )

    @property
    def is_draft(self) -> bool:
        """Check if the record is in draft status."""
        return self.status == self.DRAFT

    @property
    def is_published(self) -> bool:
        """Check if the record is in published status."""
        return self.status == self.PUBLISHED

    @property
    def is_archived(self) -> bool:
        """Check if the record is in archived status."""
        return self.status == self.ARCHIVED

    class Meta:
        abstract = True
