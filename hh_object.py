from dataclasses import dataclass


@dataclass
class HhObject:
    skills: list[str]
    area: str

    def to_list(self) -> list[any]:
        raise NotImplementedError
