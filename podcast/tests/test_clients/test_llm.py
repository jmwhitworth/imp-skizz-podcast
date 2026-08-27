from django.test import TestCase

from podcast.clients.llm import LLMClient


class LLMClient__identify_episode__TestCase(TestCase):
    def setUp(self):
        self.identifier = LLMClient()

    def test_identify_episode(self):
        cases = [
            # Standard Season & Episode
            (
                "Reacting To Extreme Sports | Imp And Skizz Podcast (S4Ep5)",
                {"is_episode": True, "season": 4, "episode": 5},
            ),
            # Season & Episode with trailing punctuation and spacing
            (
                "Remind Yourself of What You’re Grateful For | Imp And Skizz Podcast  (S2E18).",
                {"is_episode": True, "season": 2, "episode": 18},
            ),
            # Episode only (Defaults to Season 1)
            (
                "OUR FINAL EPISODE...(for now) | Imp And Skizz Podcast (Ep136)",
                {"is_episode": True, "season": 1, "episode": 136},
            ),
            # Episode only with zero-padding
            (
                "What Makes A Good Leader? | Imp And Skizz Podcast (Ep09)",
                {"is_episode": True, "season": 1, "episode": 9},
            ),
            # Title contains a Part/Pt number, but is still a valid episode
            (
                "A DOCTOR IN THE HOUSE! Pt 2 | Imp And Skizz Podcast (Ep102)",
                {"is_episode": True, "season": 1, "episode": 102},
            ),
            (
                "ANOTHER SIDE OF ZED...KRIS! Pt - 2 | Imp And Skizz Podcast (Ep51)",
                {"is_episode": True, "season": 1, "episode": 51},
            ),
            (
                "Our Thoughts on Hermitcraft Season 10 | Imp And Skizz Podcast (Ep111)",
                {"is_episode": True, "season": 1, "episode": 111},
            ),
            (
                "You Asked We Answered Part 2 | Imp And Skizz Podcast (Ep14)",
                {"is_episode": True, "season": 1, "episode": 14},
            ),
            # Invalid: Standard short/clip
            (
                "Skizz hates Minecraft",
                None,
            ),
            # Invalid: Title contains "Pt" but no valid episode marker
            (
                "Tornado Pt. 3",
                None,
            ),
            # Invalid: Special characters and no episode marker
            (
                "We're Back!...Soon™️",
                None,
            ),
        ]

        for title, expected in cases:
            with self.subTest(title=title):
                data = self.identifier.identify_episode(title)

                if expected is None:
                    self.assertIsNone(data)
                else:
                    self.assertIsNotNone(data)
                    self.assertEqual(data.is_episode, expected["is_episode"])
                    self.assertEqual(data.season, expected["season"])
                    self.assertEqual(data.episode, expected["episode"])


class LLMClient__rename_episode__TestCase(TestCase):
    def setUp(self):
        self.identifier = LLMClient()

    def test_rename_episode(self):
        cases = [
            (
                "Reacting To Extreme Sports | Imp And Skizz Podcast (S4Ep5)",
                "Reacting To Extreme Sports",
            ),
            (
                "Remind Yourself of What You’re Grateful For | Imp And Skizz Podcast  (S2E18).",
                "Remind Yourself of What You’re Grateful For",
            ),
            (
                "OUR FINAL EPISODE...(for now) | Imp And Skizz Podcast (Ep136)",
                "OUR FINAL EPISODE...(for now)",
            ),
            (
                "What Makes A Good Leader? | Imp And Skizz Podcast (Ep09)",
                "What Makes A Good Leader?",
            ),
            (
                "A DOCTOR IN THE HOUSE! Pt 2 | Imp And Skizz Podcast (Ep102)",
                "A DOCTOR IN THE HOUSE! Pt 2",
            ),
            (
                "ANOTHER SIDE OF ZED...KRIS! Pt - 2 | Imp And Skizz Podcast (Ep51)",
                "ANOTHER SIDE OF ZED...KRIS! Pt - 2",
            ),
            (
                "Our Thoughts on Hermitcraft Season 10 | Imp And Skizz Podcast (Ep111)",
                "Our Thoughts on Hermitcraft Season 10",
            ),
            (
                "You Asked We Answered Part 2 | Imp And Skizz Podcast (Ep14)",
                "You Asked We Answered Part 2",
            ),
            (
                "Skizz hates Minecraft",
                "Skizz hates Minecraft",
            ),
            (
                "Tornado Pt. 3",
                "Tornado Pt. 3",
            ),
            (
                "We're Back!...Soon™️",
                "We're Back!...Soon™️",
            ),
        ]

        for title, expected in cases:
            with self.subTest(title=title):
                new_title = self.identifier.rename_episode(title)
                self.assertEqual(new_title, expected)
