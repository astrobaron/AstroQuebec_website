import unittest

from scripts.import_seminars import build_download_url


class ImportSeminarsTests(unittest.TestCase):
    def test_build_download_url_for_google_sheet_share_link(self):
        source = "https://docs.google.com/spreadsheets/d/1RgMvotaWYA2v1OBbQIbUGdM1vXiWpkI0OZByAloRjyE/edit?usp=sharing"
        self.assertEqual(
            build_download_url(source),
            "https://docs.google.com/spreadsheets/d/1RgMvotaWYA2v1OBbQIbUGdM1vXiWpkI0OZByAloRjyE/export?format=csv&gid=0",
        )


if __name__ == "__main__":
    unittest.main()
