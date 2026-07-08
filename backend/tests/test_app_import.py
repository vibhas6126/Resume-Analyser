import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


class AppImportTests(unittest.TestCase):
    def test_app_instantiates(self) -> None:
        self.assertEqual(app.title, "ResumeIQ API")


if __name__ == "__main__":
    unittest.main()
