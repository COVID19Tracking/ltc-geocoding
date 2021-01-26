import unittest
import filecmp
import os

from nm_ar_generator import fill_in_missing

class TestFillInMissing(unittest.TestCase):

    def test_integration(self):
        test_csv = "fixtures/test_nm.csv"
        fill_in_missing(test_csv, "test")
        self.assertTrue(filecmp.cmp("filled_in_test.csv", "fixtures/expected_test_nm.csv"))
        os.remove("filled_in_test.csv")

if __name__ == '__main__':
    unittest.main()
