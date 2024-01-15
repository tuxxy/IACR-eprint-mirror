import requests
from lxml import etree
import os
import re

assert __name__ == "__main__"


def peep_paper_counts() -> dict[str, int]:
    counts = {}
    tree = etree.HTML(requests.get("https://eprint.iacr.org/byyear").text)
    lis = tree.xpath("//h3[text()='By year']/following-sibling::ul[1]/li/a")
    for li in lis:
        count = int(li.tail.strip(" ()").split()[0])
        counts[li.text] = count
    return counts

# accounts for withdrawn papers i suppose
known_deviances = {
    "2023": 1970,
    "2022": 1779,
    "2021": 1704,
    "2020": 1619,
    "2019": 1499,
    "2018": 1251,
    "2016": 1196,
    "2015": 1256,
    "2013": 882,
    "2010": 661,
    "2009": 637,
    "2006": 486,
    "2004": 377,
}


def biggest_paper_in_year(year: int, default= None) -> int:
    return max((int(s.split(".")[0]) for s in os.listdir(year)), default=default)


def check_consistency(counts: dict[str, int]) -> dict[str, str]:
    counts.update(known_deviances)
    report = {}
    for year, expected_count in counts.items():
        if not os.path.isdir(year):
            report[year] = "missing"
            continue
        contents = os.listdir(year)

        if (m := biggest_paper_in_year(year)) != expected_count:
            report[year] = f"partial (here {m} web <= {expected_count})"
    for d in os.listdir():
        if d.isnumeric() and d not in counts:
            report[d] = "time travel"
    return report


def display(report):
    for year, status in report.items():
        print(f"{year}\t{status}")


def get_item(year, ct):
    response = requests.get(f"https://eprint.iacr.org/{year}/{ct}.pdf")
    if response.status_code == 200:
        with open(f"{year}/{ct}.pdf", "wb") as f:
            f.write(response.content)
    else:
        print(f"Failed to download {year}/{ct}.pdf")


counts = peep_paper_counts()
display(report := check_consistency(counts.copy()))

for year in report:
    os.makedirs(year, exist_ok=True)
    done_so_far = biggest_paper_in_year(year, default=0)
    for ix in range(done_so_far+1, counts[year]):
        get_item(year, ix)
