import argparse
import csv
import sys
from _csv import writer
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlencode

import requests


@dataclass
class VacanciesQuery:
    search: str
    areas: list[int]
    roles: list[int]

    BASE_URL: str = "https://api.hh.ru/vacancies/"

    @classmethod
    def args_to_vacancy_query(cls, args: argparse.Namespace) -> "VacanciesQuery":
        roles: list[int] = list()
        if args.roles:
            roles = [int(it, 10) for it in args.roles]

        return cls(
            search=args.search_query,
            areas=[int(it, 10) for it in args.areas],
            roles=roles
        )

    def get_url(self) -> str:
        vacancy_query_dict: dict[any, any] = dict()
        vacancy_query_dict.update({"text": self.search})
        vacancy_query_dict.update({"area": self.areas})
        vacancy_query_dict.update({"roles": self.roles})
        vacancy_query_dict.update({"per_page": 100})
        return f"{self.BASE_URL}?{urlencode(vacancy_query_dict, doseq=True)}"


@dataclass
class Vacancy:
    id: int
    is_premium: bool
    name: str
    department: str | None
    has_test: bool
    is_response_letter_required: bool
    area: str
    salary_from: int | None
    salary_to: int | None
    type: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    url: str
    employer_name: str
    is_accredited_it_employer: bool | None
    # schedule: str
    experience: str

    # employment: str

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
            experience=data["experience"]["name"],
        )

    def to_list(self) -> list:
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
            self.experience,
        ]


@dataclass
class Vacancies:
    vacancies: list[Vacancy]

    def to_csv(self, vacancies_query: VacanciesQuery) -> None:
        table: list[list[str]] = [
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
                "Experience"
            ]
        ]
        for vacancy in self.vacancies:
            table.append(vacancy.to_list())

        with open(
                f"export_{vacancies_query.search}_{vacancies_query.areas}_{vacancies_query.roles}.csv",
                "w",
                encoding="utf-8",
                newline=""
        ) as csv_file:
            csv_writer: writer = csv.writer(csv_file)
            csv_writer.writerows(table)


def parse_args(arguments: list):
    parser = argparse.ArgumentParser(description="hh-parse - tool for parsing hh.ru")
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
    return parser.parse_args(arguments)


def main(raw_arguments: list) -> None:
    args = parse_args(raw_arguments[1:])
    vacancies_query: VacanciesQuery = VacanciesQuery.args_to_vacancy_query(args)
    vacancy_query_url: str = vacancies_query.get_url()
    num_of_pages: int = requests.get(vacancy_query_url).json()["pages"]

    vacancies_list: list[Vacancy] = list()
    for page_num in range(0, num_of_pages + 1):  #
        page_data: any = requests.get(vacancy_query_url, {"page": page_num}).json()
        for raw_vacancy in page_data["items"]:
            vacancies_list.append(Vacancy.data_to_vacancy(raw_vacancy))

    vacancies: Vacancies = Vacancies(vacancies_list)
    vacancies.to_csv(vacancies_query)


if __name__ == '__main__':
    main(sys.argv)
