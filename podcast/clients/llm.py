import logging
from typing import Optional

import litellm
from django.conf import settings
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class EpisodeData(BaseModel):
    # The reasoning field forces Chain of Thought, preventing premature negative matching
    reasoning: str = Field(
        description="Explain step-by-step if you found an 'Ep' or 'S#' indicator, and whether you should ignore 'Part/Pt'."
    )
    is_episode: bool = Field(
        description="True if an explicit episode number indicator (like Ep102 or S2E4) is present."
    )
    season: int = Field(
        default=1,
        description="The extracted season number. Default to 1 if an episode number is found but no season is specified.",
    )
    episode: Optional[int] = Field(
        default=None,
        description="The extracted episode number. Null if not an episode.",
    )


class PodcastEpisodeIdentifier:
    def __init__(
        self,
        model: str = settings.LLM_API_MODEL,
        api_base: str = settings.LLM_API_BASE,
    ):
        self.model = model
        self.api_base = api_base

    def identify_episode(self, title: str) -> Optional[EpisodeData]:
        prompt = (
            f"Extract season and episode numbers from the title.\n"
            f"CRITICAL RULES:\n"
            f"1. Valid episodes ALWAYS have an indicator like 'Ep102' or 'S4Ep5'.\n"
            f"2. If a title has a valid episode indicator (e.g., 'Ep14'), it IS an episode. Completely ignore words like 'Part 2' or 'Pt 2' if a valid 'Ep' indicator exists.\n"
            f"3. Only return is_episode: false if there is NO 'Ep' or 'S#' indicator at all (e.g., 'Tornado Pt. 3').\n"
            f"4. Ignore text like 'Season 10'. The podcast season is ONLY the 'S' prefix inside the episode bracket (e.g., S3Ep8). If it just says 'Ep111', season is 1.\n\n"
            f"Examples:\n"
            f"- 'Reacting To Extreme Sports (S4Ep5)' -> reasoning: 'Found S4Ep5.', is_episode: true, season: 4, episode: 5\n"
            f"- 'The Big Interview Pt 2 (Ep114)' -> reasoning: 'Found Ep114. Ignoring Pt 2.', is_episode: true, season: 1, episode: 114\n"
            f"- 'Story Time Pt. 4' -> reasoning: 'No Ep or S# indicator found. Only Pt.', is_episode: false, season: 1, episode: null\n"
            f"- 'Our Thoughts on Hermitcraft Season 10 (Ep111)' -> reasoning: 'Found Ep111. Ignoring Season 10 text.', is_episode: true, season: 1, episode: 111\n\n"
            f"Title to analyze: '{title}'"
        )

        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format=EpisodeData,
                api_base=self.api_base,
            )

            raw_content = response.choices[0].message.content
            data = EpisodeData.model_validate_json(raw_content)

        except (ValidationError, Exception) as e:
            logger.error(f"Failed to process video '{title}': {e}")
            return None

        if not data.is_episode or data.episode is None:
            return None

        return data
