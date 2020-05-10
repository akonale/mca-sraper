import unittest

from mc_govt_parser import DinDetail

class TestStringMethods(unittest.TestCase):
    def test_upper(self):
        detail = DinDetail("03556666", "U31909MH2018PTC312032")
        results = detail.get_parsed_results()
        print(results)
        # with open("sample_din_response.html") as f:
        #     sample_response = f.read()
        #     results = detail._parse_html(sample_response)
        #     print(results)

