import textwrap

import unittest
from beancount import loader
from beancount.parser import cmptest


class TestExampleAutoDepreciation(cmptest.TestCase):
    def test_auto_depreciation(self):
        sample = """
        option "insert_pythonpath" "True"
        plugin "auto_depreciation" "{
          'assets':'Assets:Fixed-Assets',
          'expenses':'Expenses:Depreciation',
        }"

        2020-03-01 open Assets:Cash CNY
        2020-03-01 open Assets:Fixed-Assets
        2020-03-01 open Expenses:Depreciation
        2020-03-01 open Equity:Opening-Balances

        2020-03-01 commodity LENS
            name: "Camera lens"
            assets-class: "fixed assets"

        2020-03-01 * ""
            Assets:Cash                     2000.00 CNY
            Equity:Opening-Balances

        2020-03-31 * "Test"
            Assets:Cash                     -2000.00 CNY
            Assets:Fixed-Assets        2 LENS {600.00 CNY, "Nikon"}
              useful_life: "3m"
              residual_value: 200
            Assets:Fixed-Assets        1 LENS {800.00 CNY}
              useful_life: "2m"
        """
        entries, errors, _ = loader.load_string(textwrap.dedent(sample))
        expected_entries = """
        2020-03-01 open Assets:Cash                                     CNY
        2020-03-01 open Assets:Fixed-Assets
        2020-03-01 open Expenses:Depreciation
        2020-03-01 open Equity:Opening-Balances

        2020-03-01 commodity LENS
          assets-class: "fixed assets"
          name: "Camera lens"

        2020-03-01 * 
          Assets:Cash               2000.00 CNY
          Equity:Opening-Balances  -2000.00 CNY

        2020-03-31 * "Test"
          Assets:Cash              -2000.00 CNY                                   
          Assets:Fixed-Assets        2 LENS {600.00 CNY, 2020-03-31, "Nikon"}
            useful_life: "3m"
            residual_value: 200
          Assets:Fixed-Assets        1 LENS {800.00 CNY, 2020-03-31}
            useful_life: "2m"

        2020-04-30 * "Test-auto_depreciation:Nikon"
          Assets:Fixed-Assets   -2 LENS {600.00 CNY, 2020-03-31, "Nikon"}
          Assets:Fixed-Assets    2 LENS {380 CNY, 2020-04-30, "Nikon"}   
          Expenses:Depreciation    440 CNY                                   
            useful_life: "3m"
            residual_value: 200

        2020-04-30 * "Test-auto_depreciation"
          Assets:Fixed-Assets            -1 LENS {800.00 CNY, 2020-03-31}
            useful_life: "2m"
          Assets:Fixed-Assets             1 LENS {207 CNY, 2020-04-30}   
            useful_life: "2m"
          Expenses:Depreciation  593 CNY                          
            useful_life: "2m"

        2020-05-31 * "Test-auto_depreciation:Nikon"
          Assets:Fixed-Assets   -2 LENS {380 CNY, 2020-04-30, "Nikon"}
          Assets:Fixed-Assets    2 LENS {243 CNY, 2020-05-31, "Nikon"}
          Expenses:Depreciation    274 CNY                                
            useful_life: "3m"
            residual_value: 200

        2020-05-31 * "Test-auto_depreciation"
          Assets:Fixed-Assets            -1 LENS {207 CNY, 2020-04-30}
            useful_life: "2m"
          Assets:Fixed-Assets             1 LENS {0 CNY, 2020-05-31}  
            useful_life: "2m"
          Expenses:Depreciation  207 CNY                       
            useful_life: "2m"
        
        2020-06-30 * "Test-auto_depreciation:Nikon"
          Assets:Fixed-Assets  -2 LENS {243 CNY, 2020-05-31, "Nikon"}
          Assets:Fixed-Assets   2 LENS {200 CNY, 2020-06-30, "Nikon"}
          Expenses:Depreciation    86 CNY                                
            useful_life: "3m"
            residual_value: 200

        """
        self.assertEqualEntries(expected_entries, entries)
        self.assertFalse(errors)


if __name__ == "__main__":
    unittest.main()