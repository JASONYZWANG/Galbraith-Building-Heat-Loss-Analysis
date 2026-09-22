import csv
from dataclasses import replace
import io
from pathlib import Path
import unittest

from thermal_analysis.model import analyze, export_csv, parse_filename, read_csv, severity

ROOT = Path(__file__).resolve().parents[1]


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / "data/example_observations.csv").read_text(encoding="utf-8")
        self.zones = read_csv(self.text)

    def test_historical_sample_reproduces_workbook(self):
        for zone, expected in zip(self.zones, [32.49, 17.08, 66.12]):
            self.assertAlmostEqual(analyze(zone)["proxy_w_m2"], expected)
        self.assertEqual([analyze(z)["severity"] for z in self.zones], ["Medium", "Medium", "High"])

    def test_area_changes_total_not_density_or_band(self):
        one = analyze(self.zones[0], 100)
        five = analyze(replace(self.zones[0], area_m2=5), 100)
        self.assertEqual(one["severity"], five["severity"])
        self.assertEqual(one["proxy_w_m2"], five["proxy_w_m2"])
        self.assertAlmostEqual(five["proxy_w"], one["proxy_w"] * 5)
        self.assertAlmostEqual(five["scenario_kwh"], one["scenario_kwh"] * 5)

    def test_boundary_bands(self):
        self.assertEqual([severity(x) for x in [0, 9.999, 10, 50, 50.001]], ["Low", "Low", "Medium", "Medium", "High"])

    def test_invalid_inputs_rejected(self):
        for fields in [dict(average_c=100), dict(u_value=0), dict(area_m2=-1),
                       dict(average_c=float("nan")), dict(reference_c=float("inf")),
                       dict(reference_c=-274), dict(reference_basis="unknown"), dict(material="")]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                replace(self.zones[0], **fields)
        for hours in [-1, 8761, float("nan")]:
            with self.assertRaises(ValueError):
                analyze(self.zones[0], hours)

    def test_invalid_csv_and_duplicates(self):
        for text in ["zone\nA", self.text.splitlines()[0],
                     self.text + self.text.splitlines()[1] + "\n",
                     self.text.replace("16.8,18.7", "20,18.7")]:
            with self.assertRaises(ValueError):
                read_csv(text)

    def test_filename_parsing_and_rejection(self):
        zone = parse_filename("Door(10.9 18.3 7.8 3).jpg")
        self.assertAlmostEqual(analyze(zone)["proxy_w_m2"], 66.12)
        self.assertEqual(parse_filename("Cold(-10 -5 -12 1).PNG").average_c, -10)
        for name in ["raw.jpg", "Door(10 11 9 99).jpg", "Wall(22.8 21 20.4 1).jpg"]:
            with self.assertRaises(ValueError):
                parse_filename(name)

    def test_export_preserves_inputs_and_escapes_formula_text(self):
        row = analyze(replace(self.zones[0], note="=HYPERLINK(\"bad\")"), 100)
        text = export_csv([row]).decode("utf-8-sig")
        saved = next(csv.DictReader(io.StringIO(text)))
        self.assertTrue(saved["note"].startswith("'="))
        self.assertEqual(saved["reference_basis"], "indoor_air")
        self.assertEqual(saved["scenario_hours"], "100")
        self.assertAlmostEqual(analyze(read_csv(text)[0])["proxy_w_m2"], 32.49)


if __name__ == "__main__":
    unittest.main()
