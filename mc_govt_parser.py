import csv
import sys
import traceback
from abc import abstractmethod
from random import Random
from time import sleep

import requests
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
        print("Making request: Start")
        post = requests.post(self.url, data=self.form_data, headers=self.headers, timeout=20,
                             cookies={"Cookie": "some"})
        print("Making post request: Done")
        return post

    def get_parsed_results(self):
        errors = {}
        success = {}
        try:
            post_response = self._get_http_post_results()
            if post_response.status_code != 200:
                errors["ID"] = self.pk
                errors["STATUS_CODE"] = post_response.status_code
                errors["ERROR MESSAGE"] = post_response.reason
                return success, errors
            return self._parse_html(post_response.text), errors
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            errors["ID"] = self.pk
            errors["STATUS_CODE"] = 0
            errors["ERROR MESSAGE"] = str(e)
            return success, errors


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
        print("Parsing html")

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
        post_response = self._get_http_post_results()
        soup = BeautifulSoup(post_response.text, 'html.parser')
        signatories = soup.find(id="signatories")
        dins = []
        # print(soup.prettify())
        signatory_table = signatories.find_all_next("table")
        if signatory_table is not None:
            din_rows = signatory_table[0].find_all_next("tr")
            for each in din_rows:
                all_tds = each.find_all("td")
                if all_tds is not None and len(all_tds) > 0:
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
        errored_result = []
        counter = 0
        for id in input_pks:
            counter += 1
            if counter == self.max_results:
                break
            print("{} Getting results for id: {}".format(str(counter), id))
            success_rows, error_rows = self._get_rows_for_pk(id)
            final_results.extend(success_rows)
            errored_result.extend(error_rows)
            randint = random.randint(2, 10)
            print("Sleeping for {}".format(randint))
            sleep(randint)
            print("Request done")
        self._write_csv(final_results, errored_result)

    @abstractmethod
    def _get_rows_for_pk(self, pk):
        # return each row
        # make http_request
        # parse html
        # have try catch
        pass

    def _write_csv(self, csv_dict_rows, errored_rows):
        if len(csv_dict_rows) > 0:
            print("Writing {} success rows to csv file {}".format(len(csv_dict_rows), self.output_csv))
            with open(self.output_csv, "w") as f1:
                writer = csv.DictWriter(f1, csv_dict_rows[0].keys())
                writer.writeheader()
                writer.writerows(csv_dict_rows)

        if len(errored_rows) > 0:
            error_csv = "{}_errors.csv".format(self.output_csv.replace(".csv", ""))
            print("Writing {} success rows to csv file {}".format(len(errored_rows), error_csv))
            with open(error_csv, "w") as f1:
                writer = csv.DictWriter(f1, errored_rows[0].keys())
                writer.writeheader()
                writer.writerows(errored_rows)


class LLPDataParser(CommonCompanyParser):
    def __init__(self, input_csv, output_csv, max_results):
        super().__init__(input_csv, output_csv, max_results)

    def _get_rows_for_pk(self, pk):
        llp_detail = LLPDetail(pk)
        success, error = llp_detail.get_parsed_results()
        return [success], [error]


class DinDataParser(CommonCompanyParser):
    def __init__(self, input_csv, output_csv, max_results):
        super().__init__(input_csv, output_csv, max_results)

    def _get_rows_for_pk(self, pk):
        llp_detail = LLPDetail(pk)
        din_rows_success = []
        din_rows_error = []
        try:
            dins = llp_detail.get_dins()
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            errors = {"ID": pk, "STATUS_CODE": 0, "ERROR MESSAGE": str(e)}
            din_rows_error = [errors]
            dins = []

        for din in dins:
            detail = DinDetail(din, pk)
            success, error = detail.get_parsed_results()
            if bool(success):
                din_rows_success.append(success)
            if bool(error):
                din_rows_error.append(error)
        return din_rows_success, din_rows_error

def main():
    # This is to parse "View Company or LLP Master Data"
    LLP_INPUT = "input_files/eirSeptember_2018.csv"
    LLP_OUPUT = "out_files/llp_details.csv"
    LLPDataParser(LLP_INPUT, LLP_OUPUT, 10).parse()

    # This is to parse "din details"
    DIN_INPUT = "input_files/eirSeptember_2018.csv"
    DIN_OUTPUT = "out_files/din_details.csv"
    DinDataParser(DIN_INPUT, DIN_OUTPUT, 10).parse()

if __name__ == "__main__":
    main()