from factory.django import DjangoModelFactory

from status.models import StatusModelMixin as Status


class StatusModelFactoryMixin(DjangoModelFactory):
    class Meta:
        model = Status
        abstract = True

    status = Status.PUBLISHED
