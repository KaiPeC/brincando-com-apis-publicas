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
# Criando a Sessão do Spark
ss = SparkSession.builder.getOrCreate()

# Requisições na Api para coletar os pokemons existentes
pokes = []
req_pok = 0
url = "https://pokeapi.co/api/v2/pokemon/?limit=50"


while url != None:
    response = requests.get(url)
    load_pokes = json.loads(response.content.decode("utf-8"))
    req_pok += 1

    pokes_ = load_pokes["results"]
    pokes += pokes_
    url = load_pokes["next"]

    print(f"A Requisição de nº {req_pok} coletou {len(pokes_)} Pokemons")

# Transformando a Requisição em DataFrame
df_pokes = ss.sparkContext.parallelize(pokes).map(lambda x: json.dumps(x))
df_pokes = ss.read.json(df_pokes)
# Adicionadno um Datalog com o horario da execução do processo
df_pokes = df_pokes.withColumn("datalog", sf.lit(now))
# Coletando os ID's dos Pokemons, segundo o id da URL
df_pokes = df_pokes.withColumn("id", sf.split(sf.col("url"), "/").getItem(6))
df_pokes = df_pokes.withColumn("id", df_pokes.id.cast(IntegerType()))
# Ordenando as Colunas do DF
df_pokes = df_pokes[["id", "name", "url", "datalog"]]

df_pokes.write.parquet(
    "C:/Users/kai_borges/Desktop/git_data_engineer_kaique/pokemons/transient/pokelist"
)
