from pathlib import Path
import unittest

# Initialize native dataframe extensions before starting the app's script thread.
import pandas
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class AppTests(unittest.TestCase):
    def start(self):
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        self.assertEqual(len(at.exception), 0)
        return at

    def test_example_and_empty_filter(self):
        at = self.start()
        self.assertEqual(at.metric[0].value, "32.49 W/m²")
        self.assertEqual(len(at.dataframe[0].value), 3)
        at.multiselect[0].set_value([]).run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(len(at.dataframe), 0)
        self.assertTrue(any("No observations" in i.value for i in at.info))

    def test_edit_updates_all_views_in_one_submission(self):
        at = self.start()
        next(n for n in at.number_input if n.label == "Area (m²)").set_value(2.0)
        next(n for n in at.number_input if n.label == "Assumed U-value (W/m²K)").set_value(10.0)
        at.checkbox[0].check()
        at.button[0].click().run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.metric[0].value, "57.00 W/m²")
        self.assertEqual(at.metric[1].value, "114.00 W")
        self.assertEqual(at.metric[2].value, "High")
        table = at.dataframe[0].value
        row = table[table.zone == "Glass door"].iloc[0]
        self.assertAlmostEqual(row.proxy_w, 114)
        self.assertTrue(row.flagged)
        at.selectbox[0].select("Metal door edge").run()
        at.selectbox[0].select("Glass door").run()
        self.assertEqual(at.metric[1].value, "114.00 W")

    def test_upload_sources_wait_for_input(self):
        for source in ["Upload CSV", "Upload labelled images"]:
            at = self.start()
            at.sidebar.radio[0].set_value(source).run()
            self.assertEqual(len(at.exception), 0)
            self.assertEqual(len(at.metric), 0)


if __name__ == "__main__":
    unittest.main()
