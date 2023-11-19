"""utils.py"""
from re import finditer
from lxml.html import fromstring
import requests


def get_tree(link: str) -> fromstring:
    """get tree"""
    return fromstring(requests.get(link, timeout=50, verify=False).text)


def chunker(seq, size: int) -> iter:
    """chunker
    Example: chunker([1,2,3,4,5,6,7,8], 3) -> [[1,2,3],[4,5,6],[7,8]]"""
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def camelCase(st: str) -> str:
    """
    Example: camelCase("foo bar") -> "fooBar"
    """
    output = ''.join(x for x in st.title() if x.isalnum())
    return output[0].lower() + output[1:]


def camel_case_merge(identifier: str) -> str:
    """
    Example: camel_case_merge("fooBar") -> "Foo Bar"
    """
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return " ".join([m.group(0) for m in matches]).title()


def get_id(string: str) -> str:
    """get id"""
    return "".join(x for x in string.split("=")[-1].split("&")[0] if x.isdigit())


def get_ids_from_path(tree: fromstring, path: str) -> list:
    """get ids from path"""
    ids = tree.xpath(path + ("/@href" if "/@href" not in path else ""))
    if ids and any("#" == x for x in ids):
        ids = [get_id([y for y in x.values() if "Utils" in y or ".html" in y][0]) for x in tree.xpath(path)]
    else:
        ids = [x.split("=")[-1].split("&")[0].strip() for x in ids]
    return ids


def redirect_statistics(link: str) -> str:
    """Example:
    link =
    "https://secura.e-sim.org/statistics.html?selectedSide=STOCK_COMPANY&countryId=0&statisticType=BY_STOCKS_NUMBER&page=1"
    redirect_statistics(link) ->
    https://secura.e-sim.org/stockCompanyStatistics.html?selectedSide=STOCK_COMPANY&countryId=0&statisticType=BY_STOCKS_NUMBER&page=1
    (statistics.html is locked for non-registered users)
    """
    selected_site = link.split("selectedSite=")[-1].split("&")[0]
    return link.replace("statistics.html?selectedSite=" + selected_site,
                        camelCase(selected_site) + "Statistics.html").replace("&", "?", 1)
