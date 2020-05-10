import traceback
from random import Random
from time import sleep

import requests
from html.parser import HTMLParser

import sys
from bs4 import BeautifulSoup
import csv

MAX_RESULTS = 5
OUTPUT_FILE = "otre_status.csv"
INPUT_CSV = "eirSeptember_2018.csv"

headers = {
    # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'Host': 'www.mca.gov.in',
    'Origin': 'http://www.mca.gov.in',
    'Referer': 'http://www.mca.gov.in/mcafoportal/vpdDocumentCategoryDetails.do'
}


def get_results(document, comapny_id):
    soup = BeautifulSoup(document, 'html.parser')
    # print(soup.prettify())
    all_results = []
    filing_results = soup.find(id="results")
    if filing_results is None:
        all_results.append([comapny_id, "No data", "No data"])
        return all_results
    for each in filing_results.find_all_next("tr"):
        each_result = []
        all_tds = each.find_all("td")
        if len(all_tds) > 0:
            doc_name, signed_date = all_tds
            if doc_name.string is not None and signed_date.string is not None:
                doc_name = doc_name.string.strip()
                signed_date = signed_date.string.strip()
                each_result.append(comapny_id)
                each_result.append(doc_name)
                each_result.append(signed_date)
        if len(each_result) > 1:
            all_results.append(each_result)
    return all_results


def read_ids():
    # ids = [
    #     "U74999KA2019FTC128403",
    #     "U52609KA2019PTC127249"
    # ]
    ids = []
    with open(INPUT_CSV) as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if row[1].startswith("U"):
                ids.append(row[1])
    return ids


def main():
    ids = read_ids()
    # print(ids)
    final_results = get_otre_status(ids)
    print(final_results)
    write_results(final_results)


def write_results(final_results):
    with open(OUTPUT_FILE, "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(final_results)


def get_otre_status(ids):
    random = Random()
    final_results = []
    counter = 0
    for id in ids:
        counter += 1
        if counter == MAX_RESULTS:
            break
        print("{} Getting results for id: {}".format(str(counter), id))
        API_ENDPOINT = "http://www.mca.gov.in/mcafoportal/vpdDocumentCategoryDetails.do?cinFDetails={}&companyName=&cartType&categoryName=OTRE&finacialYear=2019".format(
            id)
        try:
            print("making request")
            post = requests.post(API_ENDPOINT, headers=headers, timeout=20)
            randint = random.randint(2, 10)
            print("Sleeping for {}".format(randint))
            sleep(randint)
            print("Request done")
            results = get_results(post.text, id)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            results = [[id, "Error getting results", "Error getting results"]]
        print("Result length: {}", str(len(results)))
        final_results.extend(results)

    return final_results


if __name__ == "__main__":
    main()
