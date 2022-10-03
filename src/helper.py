import requests
from bs4 import BeautifulSoup


def citations(url):
    page = requests.get(url)
    if page.status_code != 200:
        raise ValueError("Unable to fetch profile")
    soup = BeautifulSoup(page.content, "html.parser")
    papers = len(
        soup.find("table", id="gsc_a_t")
        .find("tbody")
        .findChildren("tr", recursive=False)
    )
    elem = soup.find("table", id="gsc_rsb_st").find("tbody")
    data = {}
    for row in elem.findChildren("tr", recursive=False):
        cols = row.findChildren("td", recursive=False)
        data[cols[0].text.lower()] = int(cols[1].text)
    return {
        "papers": papers,
        "citations": data.get("citations", 0),
        "h-index": data.get("h-index", 0),
    }


def jinja_helpers():
    return {"citations": citations}
