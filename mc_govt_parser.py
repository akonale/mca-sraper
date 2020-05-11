import csv
import traceback
from abc import abstractmethod
from random import Random
from time import sleep

import requests
import sys
from bs4 import BeautifulSoup


class CommonCompanyDetail:
    ERROR_TEXT = "ERROR"

    def __init__(self, url, form_data, pk, referer):
        self.url = url
        self.form_data = form_data
        self.pk = pk
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'Host': 'www.mca.gov.in',
            'Origin': 'http://www.mca.gov.in',
            'Referer': referer,
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br"
        }

    def _get_http_post_results(self):
        # Superclass get post results
        print("Making request")
        try:
            post = requests.post(self.url, data=self.form_data, headers=self.headers, timeout=20,
                                 cookies={"Cookie": "some"})
            # todo: response code
            return post.text
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return self.ERROR_TEXT

    def get_parsed_results(self):
        html_result = self._get_http_post_results()
        # return success and error from here
        return self._parse_html(html_result)

    @abstractmethod
    def _parse_html(self, document_str):
        # returns each row of csv
        pass


class LLPDetail(CommonCompanyDetail):
    def __init__(self, cin):
        url = "http://www.mca.gov.in/mcafoportal/companyLLPMasterData.do"
        form_data = {"companyID": cin}
        referer = "http://www.mca.gov.in/mcafoportal/viewCompanyMasterData.do"
        super().__init__(url, form_data, cin, referer)
        self.cin = cin

    def _parse_html(self, document_str):
        result = {"ID": self.pk}
        if document_str == self.ERROR_TEXT:
            print("Error while fetching company detail for id: {}".format(self.pk))
            return result
        soup = BeautifulSoup(document_str, 'html.parser')
        filing_results = soup.find(id="companyMasterData")

        for each in filing_results.find_all_next("tr"):
            all_tds = each.find_all("td")
            if len(all_tds) >= 2:
                key = all_tds[0].string
                if key is not None:
                    key = key.strip().replace("\n", " ")
                    value = all_tds[1].string
                    value = '' if value is None else value.strip()
                    value.replace("\n", "")
                    result[key] = value
        return result

    def get_dins(self):
        result_html = self._get_http_post_results()
        if result_html == self.ERROR_TEXT:
            return []

        soup = BeautifulSoup(result_html, 'html.parser')
        signatories = soup.find(id="signatories")
        dins = []
        for each in signatories.find_all_next("tr"):
            all_tds = each.find_all("td")
            if all_tds[0] is not None:
                din_link = all_tds[0].find_next("a")
                if din_link is not None:
                    dins.append(din_link.string.strip())
        return dins


class DinDetail(CommonCompanyDetail):
    def __init__(self, din, cin):
        url = "http://www.mca.gov.in/mcafoportal/enquireDIN.do"
        referer = "http://www.mca.gov.in/mcafoportal/showEnquireDIN.do"
        form_data = {"DIN": din}
        super().__init__(url, form_data, cin, referer)

    def _parse_html(self, document_str):
        result = {"ID": self.pk}
        if document_str == self.ERROR_TEXT:
            print("Error while fetching company detail for id: {}".format(self.pk))
            return result
        soup = BeautifulSoup(document_str, 'html.parser')
        table_data = soup.find(id="enquireDINDetailsId")
        # print(soup.prettify())
        for each in table_data.find_all_next("tr"):
            all_tds = each.find_all("td")
            if len(all_tds) >= 2:
                key = all_tds[0].string
                if key is not None:
                    key = key.strip().replace("\n", " ")
                    value = all_tds[1].string
                    value = '' if value is None else value.strip()
                    value.replace("\n", "")
                    result[key] = value
        return result


class CommonCompanyParser:
    def __init__(self, input_csv, output_csv, max_results):
        self.input_csv = input_csv
        self.max_results = max_results
        self.output_csv = output_csv

    def _read_ids(self):
        ids = []
        with open(self.input_csv) as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                if row["CIN"] is not None:
                    ids.append(row["CIN"])
        return ids

    def parse(self):
        # main class
        # for each ids
        # random wait
        # get each row
        # add to rows
        # write csv
        input_pks = self._read_ids()
        random = Random()
        final_results = []
        counter = 0
        for id in input_pks:
            counter += 1
            if counter == self.max_results:
                break
            print("{} Getting results for id: {}".format(str(counter), id))
            print("making request")
            row = self._get_rows_for_pk(id)
            final_results.extend(row)
            randint = random.randint(2, 10)
            print("Sleeping for {}".format(randint))
            sleep(randint)
            print("Request done")
        self._write_csv(final_results)

    @abstractmethod
    def _get_rows_for_pk(self, pk):
        # return each row
        # make http_request
        # parse html
        # have try catch
        pass

    def _write_csv(self, csv_dict_rows):
        print("Writing to csv file {}".format(self.output_csv))
        headers = csv_dict_rows[0].keys()
        with open(self.output_csv, "w") as f1:
            writer = csv.DictWriter(f1, headers)
            writer.writeheader()
            writer.writerows(csv_dict_rows)


class LLPDataParser(CommonCompanyParser):
    def __init__(self, input_csv, output_csv, max_results):
        super().__init__(input_csv, output_csv, max_results)

    def _get_rows_for_pk(self, pk):
        llp_detail = LLPDetail(pk)
        return [llp_detail.get_parsed_results()]


class DinDataParser(CommonCompanyParser):
    def __init__(self, input_csv, output_csv, max_results):
        super().__init__(input_csv, output_csv, max_results)

    def _get_rows_for_pk(self, pk):
        llp_detail = LLPDetail(pk)
        dins = llp_detail.get_dins()
        din_rows = []
        for din in dins:
            detail = DinDetail(din, pk)
            results = detail.get_parsed_results()
            din_rows.append(results)
        return din_rows
