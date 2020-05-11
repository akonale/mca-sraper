import csv

from bs4 import BeautifulSoup


def get_results(document):
    soup = BeautifulSoup(document, 'html.parser')
    filing_results = soup.find(id="companyMasterData")
    result = {}
    for each in filing_results.find_all_next("tr"):
        all_tds = each.find_all("td")
        if len(all_tds) >= 2:
            key = all_tds[0].string
            if key is not None:
                key = key.strip().replace("\n"," ")
                value = all_tds[1].string
                value = '' if value is None else value.strip()
                value.replace("\n", "")
                result[key] = value
    return result

def parse_result_html():
    with open("sample_llp_response.html") as f:
        document = f.read()
        result_dict = get_results(document)
        return result_dict


def write_results_csv(result_dict_array):
    headers = result_dict_array[0].keys()
    with open("sample_output.csv", "w") as f1:
        writer = csv.DictWriter(f1, headers)
        writer.writeheader()
        writer.writerows(result_dict_array)

def main():
    result_dict = parse_result_html()
    write_results_csv([result_dict])


if __name__ == '__main__':
    main()