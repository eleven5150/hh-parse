import argparse
import sys

import requests

from vacancies import VacanciesQuery, Vacancy, Vacancies


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
        if "items" in page_data:
            for raw_vacancy in page_data["items"]:
                vacancies_list.append(Vacancy.data_to_vacancy(raw_vacancy))

    vacancies: Vacancies = Vacancies(vacancies_list)
    vacancies.to_csv(vacancies_query)


if __name__ == '__main__':
    main(sys.argv)
