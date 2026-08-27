import base64
import logging
from typing import Optional

import litellm
from django.conf import settings
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EpisodeIdentityData(BaseModel):
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


class EpisodeRenamedData(BaseModel):
    reasoning: str = Field(
        description="Explain step-by-step what suffix needs to be removed, or if the title should be left exactly as is."
    )
    new_title: str = Field(
        description="The clean title. Everything from the '|' onward must be removed. If no '|' exists, output the original string exactly."
    )


class LLMClient:
    def __init__(
        self,
        model: Optional[str] = None,
        api_base: Optional[str] = None,
    ):
        self.model = model or settings.LLM_API_MODEL
        self.api_base = api_base or settings.LLM_API_BASE

        if settings.LLM_API_PROXY_USER and settings.LLM_API_PROXY_PASSWORD:
            auth_str = (
                f"{settings.LLM_API_PROXY_USER}:{settings.LLM_API_PROXY_PASSWORD}"
            )
            b64_auth = base64.b64encode(auth_str.encode()).decode("utf-8")
            self.headers = {"Authorization": f"Basic {b64_auth}"}
        else:
            self.headers = {}

    def _complete(self, prompt: str, response_model: type[BaseModel]) -> BaseModel:
        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_model,
            api_base=self.api_base,
            extra_headers=self.headers,
        )
        raw_content = response.choices[0].message.content
        return response_model.model_validate_json(raw_content)

    def identify_episode(self, title: str) -> Optional[EpisodeIdentityData]:
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
            data = self._complete(prompt, EpisodeIdentityData)
        except Exception as e:
            logger.error(f"Failed to process video '{title}': {e}")
            return None

        if not data.is_episode or data.episode is None:
            return None

        return data

    def rename_episode(self, title: str) -> str:
        prompt = (
            f"Clean the episode title by removing the podcast branding suffix.\n"
            f"CRITICAL RULES:\n"
            f"1. Find the pipe character '|'. Remove the '|' and ALL text after it (e.g., '| The Fake Podcast (S4Ep5)').\n"
            f"2. Remove any trailing spaces after making the cut.\n"
            f"3. If there is no '|' character in the title, you MUST return the exact original title unmodified.\n\n"
            f"Examples:\n"
            f"- 'The Best Gaming Moments | Fun Time Podcast (S3Ep12)' -> reasoning: 'Found pipe. Removing | and everything after.', new_title: 'The Best Gaming Moments'\n"
            f"- 'Learning to Cook with Chef Bob | The Cooking Show  (S1E4).' -> reasoning: 'Found pipe. Removing | and everything after.', new_title: 'Learning to Cook with Chef Bob'\n"
            f"- 'Wait, what just happened?! 🤯' -> reasoning: 'No pipe character found. Returning original.', new_title: 'Wait, what just happened?! 🤯'\n"
            f"- 'The Big Finale Pt 2 | Drama Cast (Ep99)' -> reasoning: 'Found pipe. Removing | and everything after.', new_title: 'The Big Finale Pt 2'\n\n"
            f"Title to rename: '{title}'"
        )

        try:
            data = self._complete(prompt, EpisodeRenamedData)
        except Exception as e:
            logger.error(f"Failed to rename episode '{title}': {e}")
            return title

        return data.new_title
