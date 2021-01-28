import unittest
import filecmp
import os

from fill_in_missing_dates import fill_in_missing_dates

class TestFillInMissingDates(unittest.TestCase):

    def test_integration(self):
        test_csv = "fixtures/state_with_missing_dates.csv"
        fill_in_missing_dates(test_csv, "test_state")
        self.assertTrue(filecmp.cmp("test_state_all_dates.csv", "fixtures/expected_state_with_missing_dates.csv"))
        os.remove("test_state_all_dates.csv")

if __name__ == '__main__':
    unittest.main()
