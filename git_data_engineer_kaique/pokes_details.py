import findspark

findspark.init()

# Importando Bibliotecas necessárias
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
import pyspark.sql.functions as sf
from datetime import datetime as dt
from itertools import chain
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    ArrayType,
    BooleanType,
)
import requests
import json

now = dt.now()

ss = SparkSession.builder.getOrCreate()

df_pokes = ss.read.parquet(
    "C:/Users/kai_borges/Desktop/git_data_engineer_kaique/pokemons/transient/pokelist"
)


def get_pokemon_data(dicio, name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name}"
    response = requests.get(url)
    pokemon = response.json()
    data = {
        "id": pokemon["id"],
        "name": pokemon["name"],
        "is_default": pokemon["is_default"],
        "experience": pokemon["base_experience"],
        "weight": pokemon["weight"],
        "type": [t["type"]["name"] for t in pokemon["types"]],
        "height": pokemon["height"],
        "speed": pokemon["stats"][0]["base_stat"],
        "special_defense": pokemon["stats"][1]["base_stat"],
        "special_attack": pokemon["stats"][2]["base_stat"],
        "defense": pokemon["stats"][3]["base_stat"],
        "attack": pokemon["stats"][4]["base_stat"],
        "hp": pokemon["stats"][5]["base_stat"],
    }

    dicio = dicio.append(data)

    return dicio


schema = StructType(
    [
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), True),
        StructField("is_default", BooleanType(), True),
        StructField("experience", IntegerType(), True),
        StructField("weight", IntegerType(), True),
        StructField("type", ArrayType(StringType()), True),
        StructField("height", IntegerType(), True),
        StructField("speed", IntegerType(), True),
        StructField("special_defense", IntegerType(), True),
        StructField("special_attack", IntegerType(), True),
        StructField("defense", IntegerType(), True),
        StructField("attack", IntegerType(), True),
        StructField("hp", IntegerType(), True),
    ]
)

collect = df_pokes.rdd.toLocalIterator()
list_poke = []
req = 0
for row in collect:
    data = get_pokemon_data(list_poke, row["name"])
    req += 1
    print(f"Na Req {req}, coletamos os dados do:  " + row["name"])

df_details = ss.createDataFrame(list_poke, schema=schema)

df_details.write.parquet(
    "C:/Users/kai_borges/Desktop/git_data_engineer_kaique/pokemons/transient/poke_details"
)
