import json
from urllib.request import urlopen


def get_brasilio_data(dataset, table, limit=None):
    url = f"https://brasil.io/api/dataset/{dataset}/{table}/data"
    if limit:
        url += f"?page_size={limit}"

    finished = False
    data = []
    while not finished:
        response = urlopen(url)
        response_data = json.loads(response.read())
        data.extend(response_data["results"])
        url = response_data["next"]
        if not url:
            finished = True
    return data


def filter_rows(data, **kwargs):
    for row in data:
        if all(row[key] == value for key, value in kwargs.items()):
            yield row


boletins = get_brasilio_data("covid19", "boletim")
casos = get_brasilio_data("covid19", "caso")
state_rows = list(filter_rows(casos, is_last=True, place_type="state"))
city_rows = list(filter_rows(casos, is_last=True, place_type="city"))

confirmados_estados = sum(row["confirmed"] for row in state_rows)
confirmados_municipios = sum(row["confirmed"] for row in city_rows)
mortes_estados = sum(row["deaths"] for row in state_rows)
mortes_municipios = sum(row["deaths"] for row in city_rows)
print(f"*DADOS ATUALIZADOS*")
print()
print(f"- {len(boletins)} boletins capturados")
print(f"- {confirmados_estados} casos confirmados (estado)")
print(f"- {confirmados_municipios} casos confirmados (municípios)")
print(f"- {mortes_estados} mortes (estado)")
print(f"- {mortes_municipios} mortes (municípios)")