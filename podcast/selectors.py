from .models import Podcast


def podcast_get_season_numbers() -> list[int]:
    return list(
        Podcast.objects.order_by("season")
        .distinct("season")
        .values_list("season", flat=True)
    )
