# hh-parse

Утилита для получения данных о вакансиях и резюме с hh.ru

## Установка

Необходим Python 3.12

Windows

```shell
git clone https://github.com/eleven5150/hh-parse.git
cd ./hh-parse
python -m venv venv
./venv/Scripts/activate.ps1
pip install -r ./requirements.txt
```

Linux

```bash
git clone https://github.com/eleven5150/hh-parse.git
cd ./hh-parse
python -m venv venv
source ./venv/bin/activate
pip install -r ./requirements.txt
```

# Утилиты

## vacancies_tool

Утилита для получения данных о вакансиях. На выходе создает csv файл с ними.

Команда для запуска

```shell
python . vacancies_tool
```

### Аргументы

Не являются обязательными

| Аргумент               | Описание                                                                                                                                              |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-s`, `--search_query` | Поисковый запрос по вакансиям                                                                                                                         |
| `-a`, `--areas`        | Фильтр по регионам, указываются коды из [справочника](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-countries) через пробел   |
| `-r`, `--roles`        | Фильтр по специализациям, указываются коды из [справочника](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-skills)через пробел |
| `-h`, `--help`         | Выводит подсказку по использованию аргументов                                                                                                         |

Пример использования аргументов

```shell
python . vacancies_tool -a 1 2019 -r 1 2 3 10 12 34 37 55 163 68 70 71 99 170
```

## resumes_tool

Утилита для получения данных о резюме пользователей. Данные получаются только те, что доступны в открытом доступе. Для
получения данных не требуется генерация токена. На выходе создает csv файл.

Команда для запуска

```shell
python . resumes_tool
```

### Аргументы

Не являются обязательными

| Аргумент               | Описание                                                                                                                                              |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-s`, `--search_query` | Поисковый запрос по резюме                                                                                                                            |
| `-n`, `--num_of_pages` | Количество страниц с резюме, которые будут получены (на одной странице 20 резюме)                                                                     |
| `-a`, `--areas`        | Фильтр по регионам, указываются коды из [справочника](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-countries) через пробел   |
| `-r`, `--roles`        | Фильтр по специализациям, указываются коды из [справочника](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/operation/get-skills)через пробел |
| `-h`, `--help`         | Выводит подсказку по использованию аргументов                                                                                                         |

Пример использования аргументов

```shell
python . resumes_tool -n 50 -a 1 2019 -r 1 2 3 10 12 34 37 55 163 68 70 71 99 170
```