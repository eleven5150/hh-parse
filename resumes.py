import argparse
import csv
import re
from _csv import writer
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
        resumes_query_dict.update({"filter_exp_period": "all_time"})
        resumes_query_dict.update({"relocation": "living"})
        resumes_query_dict.update({"gender": "unknown"})
        resumes_query_dict.update({"area": self.areas})
        resumes_query_dict.update({"professional_role": self.roles})
        if page_num != 0:
            resumes_query_dict.update({"page": page_num})
        return f"{self.BASE_URL}?{urlencode(resumes_query_dict, doseq=True)}"


@dataclass
class Resume:
    id: str
    title: str
    area: str
    age: int | None
    gender: str
    salary: int | None
    experience: int
    skills: list[str]

    @classmethod
    def html_to_resume(cls, resume_id: str, resume_page_soup: BeautifulSoup) -> "Resume":
        tags_with_title: ResultSet = resume_page_soup.find_all("span", {"data-qa": "resume-block-title-position"})
        title: str = tags_with_title[0].get_text()
        tags_with_area: ResultSet = resume_page_soup.find_all("span", {"data-qa": "resume-personal-address"})
        area: str = tags_with_area[0].get_text()
        tags_with_age: ResultSet = resume_page_soup.find_all("span", {"data-qa": "resume-personal-age"})
        age: int | None = None
        if len(tags_with_age) > 0:
            age = int(tags_with_age[0].get_text()[:2], 10)
        tags_with_gender: ResultSet = resume_page_soup.find_all("span", {"data-qa": "resume-personal-gender"})
        gender: str = tags_with_gender[0].get_text()
        tags_with_salary: ResultSet = resume_page_soup.find_all("span", {"data-qa": "resume-block-salary"})
        salary: int = 0
        if len(tags_with_salary) > 0:
            salary_parts: list[str] = tags_with_salary[0].get_text().split("\u2009")
            salary_parts[-1] = salary_parts[-1][:3]
            salary = int(''.join(salary_parts), 10)
        tags_with_experience: ResultSet = resume_page_soup.find_all("div", {"data-qa": "resume-block-experience"})
        experience: int = 0
        if len(tags_with_experience) > 0:
            experience_raw: str = tags_with_experience[0].contents[0].get_text()
            experience_numbers_str: list[str] = re.findall(r"\d+", experience_raw)
            experience_numbers: list[int] = [int(it, 10) for it in experience_numbers_str]
            if len(experience_numbers) == 2:
                experience = experience_numbers[0] * 12 + experience_numbers[1]
            elif len(experience_numbers) == 1:
                if len(re.findall(r"месяц", experience_raw)) > 0:
                    experience = experience_numbers[0]
                else:
                    experience = experience_numbers[0] * 12

        tags_with_skills: ResultSet = resume_page_soup.find_all("span", {
            "class": "bloko-tag__section bloko-tag__section_text"})
        skills: list[str] = list()
        for tag in tags_with_skills:
            skills.append(tag.get_text())
        return cls(
            id=resume_id,
            title=title,
            area=area,
            age=age,
            gender=gender,
            salary=salary,
            experience=experience,
            skills=skills,
        )

    def to_list(self) -> list:
        return [
            self.id,
            self.title,
            self.area,
            self.age if self.age else "None",
            self.gender,
            self.salary if self.salary else "None",
            self.experience,
            *self.skills,
        ]


@dataclass
class Resumes:
    resumes: list[Resume]

    def to_csv(self, resumes_query: ResumesQuery) -> None:
        table: list[list[str]] = [
            [
                "ID",
                "Title",
                "Area",
                "Age",
                "Gender",
                "Salary",
                "Experience (Months)",
            ]
        ]

        for resume in self.resumes:
            table.append(resume.to_list())

        rows_length: list[int] = [len(it) for it in table]
        max_length: int = max(rows_length)
        for it in range(max_length - len(table[0])):
            table[0].append(f"Skill {it + 1}")

        with open(
                f"export_resumes_{resumes_query.areas}_{resumes_query.roles}.csv",
                "w",
                encoding="utf-8",
                newline=""
        ) as csv_file:
            csv_writer: writer = csv.writer(csv_file)
            csv_writer.writerows(table)


def resumes_subparser(subparser):
    parser = subparser.add_parser("resumes_tool", description="Tool for parsing resumes")
    parser.add_argument("-n", "--num_of_pages",
                        type=int,
                        required=True,
                        help="Num of pages to parse")
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
    resumes_list: list[Resume] = list()
    for page_num in range(0, args.num_of_pages):
        query_url: str = resumes_query.get_url(page_num)
        print(query_url)
        resumes_page_data: str = requests.get(query_url, headers=REQUEST_HEADERS).text
        resumes_page_soup: BeautifulSoup = BeautifulSoup(resumes_page_data, features="lxml", from_encoding="utf-8")
        tags_with_link: ResultSet = resumes_page_soup.find_all("a", {"data-qa": "serp-item__title"})
        for tag in tags_with_link:
            resume_id: str = RE_COMPILED.search(tag["href"]).group(1).strip()
            resume_url: str = f"{RESUME_URL}{resume_id}"
            resume_page_data: str = requests.get(resume_url, headers=REQUEST_HEADERS).text
            resume_page_soup: BeautifulSoup = BeautifulSoup(resume_page_data, features="lxml", from_encoding="utf-8")
            resumes_list.append(Resume.html_to_resume(resume_id, resume_page_soup))

    vacancies: Resumes = Resumes(resumes_list)
    vacancies.to_csv(resumes_query)
