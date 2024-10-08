import csv
from _csv import writer
from dataclasses import dataclass

from hh_object import HhObject
from query import Query


@dataclass
class Items:
    items: list[HhObject]

    def to_csv(self, query: Query, table: list[list[str]]) -> None:
        for item in self.items:
            table.append(item.to_list())

        rows_length: list[int] = [len(it) for it in table]
        max_length: int = max(rows_length)
        for it in range(max_length - len(table[0])):
            table[0].append(f"Skill {it + 1}")

        with open(
                f"export_{type(self).__name__.lower()}_{query.areas}_{query.roles}.csv",
                "w",
                encoding="utf-8",
                newline=""
        ) as csv_file:
            csv_writer: writer = csv.writer(csv_file)
            csv_writer.writerows(table)
