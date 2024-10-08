import argparse
import json
import requests

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlencode

from hh_object import HhObject
from items import Items
from query import Query

VACANCIES_TABLE_HEADER: list[list[str]] = [
    [
        "ID",
        "Is Premium",
        "Name",
        "Department",
        "Has test",
        "Is response letter required",
        "Area",
        "Salary from",
        "Salary to",
        "Type",
        "Created at",
        "Updated at",
        "Is archived",
        "URL",
        "Employer name",
        "Is accredited it employer",
        "Schedule",
        "Experience",
        "Employment"
    ]
]


def vacancies_subparser(subparser):
    parser = subparser.add_parser("vacancies_tool", description="Tool for parsing vacancies")
    parser.add_argument("-s", "--search_query",
                        type=str,
                        help="Search query")
    parser.add_argument("-a", "--areas",
                        type=str,
                        nargs="+",
                        help="Area for search")
    parser.add_argument("-r", "--roles",
                        type=str,
                        nargs="+",
                        help="List of roles")

    return parser.set_defaults(func=tool_entrypoint)


@dataclass
class VacanciesQuery(Query):
    BASE_URL: str = "https://api.hh.ru/vacancies/"

    def get_url(self) -> str:
        vacancy_query_dict: dict[any, any] = super().get_query("roles")
        vacancy_query_dict.update({"text": ""})
        vacancy_query_dict.update({"per_page": 100})
        return f"{self.BASE_URL}?{urlencode(vacancy_query_dict, doseq=True)}"


@dataclass
class Vacancy(HhObject):
    id: int
    is_premium: bool
    name: str
    department: str | None
    has_test: bool
    is_response_letter_required: bool
    salary_from: int | None
    salary_to: int | None
    type: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    url: str
    employer_name: str
    is_accredited_it_employer: bool | None
    schedule: str
    experience: str
    employment: str

    @classmethod
    def data_to_vacancy(cls, data: any) -> "Vacancy":
        department: str | None = None
        if data["department"]:
            department = data["department"]["name"]

        salary_from: int | None = data["salary"]["from"] if data["salary"] and data["salary"]["from"] else None
        salary_to: int | None = data["salary"]["to"] if data["salary"] and data["salary"]["to"] else None
        if data["salary"] and data["salary"]["gross"]:
            if salary_from:
                salary_from *= 0.87
            if salary_to:
                salary_to *= 0.87

        return cls(
            id=data["id"],
            is_premium=data["premium"],
            name=data["name"],
            department=department,
            has_test=data["has_test"],
            is_response_letter_required=data["response_letter_required"],
            area=data["area"]["name"],
            salary_from=salary_from,
            salary_to=salary_to,
            type=data["type"]["name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["published_at"]),
            is_archived=data["archived"],
            url=data["alternate_url"],
            employer_name=data["employer"]["name"],
            is_accredited_it_employer=data["employer"]["accredited_it_employer"] if "accredited_it_employer" in data[
                "employer"] else None,
            schedule=data["schedule"]["name"],
            experience=data["experience"]["name"],
            employment=data["employment"]["name"],
            skills=[it["name"] for it in data["key_skills"]] if data["key_skills"] else [None],
        )

    def to_list(self) -> list[any]:
        return [
            self.id,
            self.is_premium,
            self.name,
            self.department if self.department else "None",
            self.has_test,
            self.is_response_letter_required,
            self.area,
            self.salary_from if self.salary_from else "None",
            self.salary_to if self.salary_to else "None",
            self.type,
            self.created_at,
            self.updated_at,
            self.is_archived,
            self.url,
            self.employer_name,
            self.is_accredited_it_employer if self.is_accredited_it_employer else "None",
            self.schedule,
            self.experience,
            self.employment,
            *self.skills,
        ]


@dataclass
class Vacancies(Items):
    items: list[Vacancy]


def tool_entrypoint(args: argparse.Namespace) -> None:
    vacancies_query: VacanciesQuery = VacanciesQuery.args_to_vacancy_query(args)
    vacancies_query_url: str = vacancies_query.get_url()
    print(f"Vacancies query URL: {vacancies_query_url}")
    num_of_pages: int = json.loads(requests.get(vacancies_query_url).text)["pages"]

    vacancies_list: list[Vacancy] = list()
    for page_num in range(0, num_of_pages + 1):
        page_data: any = json.loads(requests.get(vacancies_query_url, {"page": page_num}).text)
        if "items" in page_data:
            for raw_vacancy_short in page_data["items"]:
                vacancy_query_url: str = f"{vacancies_query.BASE_URL}{raw_vacancy_short['id']}"
                print(f"Vacancy query URL: {vacancies_query_url}")
                raw_vacancy_full: any = json.loads(
                    requests.get(
                        vacancy_query_url
                    ).text
                )
                if "id" in raw_vacancy_full:  # TODO: fix captcha
                    vacancies_list.append(Vacancy.data_to_vacancy(raw_vacancy_full))

    vacancies: Vacancies = Vacancies(vacancies_list)
    vacancies.to_csv(vacancies_query, VACANCIES_TABLE_HEADER)
