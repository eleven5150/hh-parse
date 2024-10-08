import argparse
from dataclasses import dataclass
from urllib.parse import urlencode

@dataclass
class Query:
    text: str
    areas: list[int]
    roles: list[int]

    @classmethod
    def args_to_vacancy_query(cls, args: argparse.Namespace) -> "Query":
        text: str = ""
        if args.search_query:
            text = args.search_query
        areas: list[int] = list()
        if args.areas:
            areas = [int(it, 10) for it in args.areas]
        roles: list[int] = list()
        if args.roles:
            roles = [int(it, 10) for it in args.roles]

        return cls(
            text=text,
            areas=areas,
            roles=roles
        )

    def get_query(self) -> dict[any, any]:
        query_dict: dict[any, any] = dict()
        if len(self.text) > 0:
            query_dict.update({"text": self.text})
        if len(self.areas) > 0:
            query_dict.update({"area": self.areas})
        if len(self.roles) > 0:
            query_dict.update({"professional_role": self.roles})
        return query_dict