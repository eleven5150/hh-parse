import argparse
import re
from dataclasses import dataclass
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup, ResultSet

from query import Query

RE_COMPILED: re.Pattern[str] = re.compile(r"resume\/(.+)\?")

RESUME_URL: str = "https://hh.ru/resume/"

REQUEST_HEADERS: dict[str, str] = {
    "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}


@dataclass
class ResumesQuery(Query):
    BASE_URL: str = "https://hh.ru/search/resume"

    def get_url(self, page_num: int) -> str:
        resumes_query_dict: dict[any, any] = dict()
        resumes_query_dict.update({"search_period": 0})
        resumes_query_dict.update({"order_by": "relevance"})
        resumes_query_dict.update({"area": self.areas})
        resumes_query_dict.update({"filter_exp_period": "all_time"})
        resumes_query_dict.update({"relocation": "living_or_relocation"})
        resumes_query_dict.update({"gender": "unknown"})
        resumes_query_dict.update({"professional_role": self.roles})
        resumes_query_dict.update({"items_on_page": 100})
        resumes_query_dict.update({"page": page_num})
        return f"{self.BASE_URL}?{urlencode(resumes_query_dict, doseq=True)}"


def resumes_subparser(subparser):
    parser = subparser.add_parser("resumes_tool", description="Tool for parsing resumes")
    parser.add_argument("-s", "--search_query",
                        type=str,
                        required=True,
                        help="Search query")
    parser.add_argument("-a", "--areas",
                        type=str,
                        required=True,
                        nargs="+",
                        help="Area for search")
    parser.add_argument("-r", "--roles",
                        type=str,
                        nargs="+",
                        help="List of roles")

    return parser.set_defaults(func=tool_entrypoint)


def tool_entrypoint(args: argparse.Namespace) -> None:
    resumes_query: ResumesQuery = ResumesQuery.args_to_vacancy_query(args)
    for page_num in range(1, 51):
        query_url: str = resumes_query.get_url(page_num)
        page_data: str = requests.get(query_url, headers=REQUEST_HEADERS).text
        soup: BeautifulSoup = BeautifulSoup(page_data, features="lxml", from_encoding="utf-8")
        tags_with_link: ResultSet = soup.find_all("a", {"data-qa": "serp-item__title"})
        for tag in tags_with_link:
            resume_id: str = RE_COMPILED.search(tag["href"]).group(1).strip()
            resume_url: str = f"{RESUME_URL}{resume_id}"
            resume_page_data: str = requests.get(resume_url, headers=REQUEST_HEADERS).text
