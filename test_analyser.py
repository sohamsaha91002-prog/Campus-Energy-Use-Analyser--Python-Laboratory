import unittest
import numpy as np
from energy_analyser import validate_reading, compute_moving_average, MeterRecord


class TestCampusEnergyAnalyser(unittest.TestCase):

    def test_validate_reading_cases(self):
        self.assertEqual(validate_reading("450.5"), (450.5, "VALID"))
        self.assertEqual(validate_reading("-15.0"), (-15.0, "NEGATIVE_ERROR"))
        self.assertEqual(validate_reading(""), (None, "MISSING"))
        self.assertEqual(validate_reading("2500.0"), (2500.0, "ABNORMAL_SPIKE"))
        self.assertEqual(validate_reading("abc"), (None, "INVALID_FORMAT"))

    def test_meter_record_special_methods(self):
        meter = MeterRecord("Test_Block")
        meter.add_reading("2026-08-01", "400")
        meter.add_reading("2026-08-02", "-10")
        meter.add_reading("2026-08-03", "500")

        # Test _len, __getitem, and ___iter__
        self.assertEqual(len(meter), 3)
        self.assertEqual(meter[0]["kwh"], 400.0)
        statuses = [entry["status"] for entry in meter]
        self.assertEqual(statuses, ["VALID", "NEGATIVE_ERROR", "VALID"])

    def test_moving_average_numpy(self):
        arr = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        ma = compute_moving_average(arr, window=3)
        np.testing.assert_allclose(ma, np.array([20.0, 30.0, 40.0]))


if __name__ == "__main__":
    unittest.main()