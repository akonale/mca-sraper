import unittest

from mc_govt_parser import DinDetail, LLPDetail, CommonCompanyParser


# ids = [
#     "U74999KA2019FTC128403",
#     "U52609KA2019PTC127249"
# ]

class TestMcaParser(unittest.TestCase):
    def test_din_parse_html(self):
        detail = DinDetail("03556666", "U31909MH2018PTC312032")
        # results = detail.get_parsed_results()
        # print(results)
        with open("sample_din_response.html") as f:
            sample_response = f.read()
            results = detail._parse_html(sample_response)
            print(results)


    def test_cin_parse_html(self):
        llp_detail = LLPDetail("U31909MH2018PTC312032")
        with open("sample_llp_response.html") as f:
            result = llp_detail._parse_html(f.read())
            print(result)

    def test_company_parser(self):
        class TestComanyParser(CommonCompanyParser):
            def __init__(self):
                super().__init__("eirSeptember_2018.csv", "test_out.csv", 3)

            def _get_rows_for_pk(self, pk):
                return [{"ID": pk, "RANDOM": "foo"}]

        parser = TestComanyParser()
        parser.parse()


        ####### integration ##################
    # def test_din_request(self):
    #     detail = DinDetail("03556666", "U31909MH2018PTC312032")
    #     results = detail.get_parsed_results()
    #     print(results)

    #     llp_detail = LLPDetail("U31909MH2018PTC312032")
    #     results = llp_detail.get_parsed_results()
    #     print(results)


