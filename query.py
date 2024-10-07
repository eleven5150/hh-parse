import argparse
from dataclasses import dataclass
from urllib.parse import urlencode

@dataclass
class Query:
    areas: list[int]
    roles: list[int]

    @classmethod
    def args_to_vacancy_query(cls, args: argparse.Namespace) -> "Query":
        roles: list[int] = list()
        if args.roles:
            roles = [int(it, 10) for it in args.roles]

        return cls(
            areas=[int(it, 10) for it in args.areas],
            roles=roles
        )

    def get_query(self) -> dict[any, any]:
        query_dict: dict[any, any] = dict()
        query_dict.update({"area": self.areas})
        query_dict.update({"roles": self.roles})
        return query_dict