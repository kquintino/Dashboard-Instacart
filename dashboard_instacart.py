### NESTE ARQUIVO IREMOS FAZER UMA DASHBOARD USANDO MATPLOTLIB E DEPOIS STREAMLIT NO RENDER PARA CRIAR UM APP DE FACIL VIZUALIZAÇÃO PARA OS DIRETORES.

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

df_orders = pd.read_csv(BASE_DIR / "orders.csv", sep=";")
df_products = pd.read_csv(BASE_DIR / "products.csv", sep=";")
df_aisles = pd.read_csv(BASE_DIR / "aisles.csv", sep=";")
df_departments = pd.read_csv(BASE_DIR / "departments.csv", sep=";")
df_order_products = pd.read_csv(BASE_DIR / "order_products.csv", sep=";")

print(df_orders[df_orders.duplicated()])
print(df_orders[(df_orders["order_dow"] == 3) & (df_orders["order_hour_of_day"] == 2)])

df_orders = df_orders.drop_duplicates()
df_orders.info()
print(df_orders[df_orders.duplicated()])
print(df_orders[df_orders["order_id"].duplicated()])

print(df_products[df_products.duplicated()])
print(df_products[df_products["product_id"].duplicated()])

df_products["product_name"] = df_products["product_name"].str.lower()
print(df_products[df_products["product_name"].duplicated()].sample(10))
print(df_products.dropna(subset=["product_name"])["product_name"].duplicated().sum())

print(df_departments[df_departments.duplicated()])
print(df_departments[df_departments["department_id"].duplicated()])

print(df_aisles[df_aisles.duplicated()])
print(df_aisles[df_aisles["aisle_id"].duplicated()])

print(df_order_products[df_order_products.duplicated()])
print(df_order_products["add_to_cart_order"].isnull().sum())

print(df_products[df_products["product_name"].isna()])

print((df_products["aisle_id"] == 100).sum())

print((df_products["department_id"] == 21).sum())

print(
    df_products[(df_products["department_id"] == 21) & (df_products["aisle_id"] == 100)]
)

df_products.fillna("Unknown", inplace=True)

print(df_orders["days_since_prior_order"].isna().value_counts())
print(
    df_orders[
        (df_orders["order_number"] == 1) & (df_orders["days_since_prior_order"].isna())
    ]
)

print((df_orders["order_number"] >= 2).isna().sum())

print(df_order_products.isna().sum())
print(df_order_products["order_id"].agg(["min", "max"]))
print()
print(df_order_products["product_id"].agg(["min", "max"]))
print()
print(df_order_products["add_to_cart_order"].agg(["min", "max"]))
print()
print(df_order_products["reordered"].agg(["min", "max"]))

nan_numbers_id = df_order_products.loc[
    df_order_products["add_to_cart_order"].isna(), "order_id"
].nunique()
print(nan_numbers_id)

# Todos os pedidos com valores ausentes contêm mais de 64 produtos?
print(
    df_order_products[df_order_products["add_to_cart_order"].isna()]
    .groupby("order_id")["product_id"]
    .count()
    .min()
    > 64
)
# Resposta: Não!

# Agrupe os pedidos com dados ausentes por ID de pedido
print(
    df_order_products[df_order_products["add_to_cart_order"].isna()]
    .groupby("order_id")
    .count()
)


# Conte o número de 'product_id' em cada pedido e verifique o valor mínimo da contagem
print(
    df_order_products[df_order_products["add_to_cart_order"].isna()]
    .groupby("order_id")["product_id"]
    .count()
    .min()
)

# Substitua valores ausentes na coluna 'add_to_cart_order' por 999 e converta a coluna para o tipo integer
df_order_products["add_to_cart_order"] = (
    df_order_products["add_to_cart_order"].fillna(999).astype(int)
)
# df_order_products['add_to_cart_order'] = pd.to_numeric(df_order_products['add_to_cart_order'], errors= 'coerce').astype('int64')
print(df_order_products["add_to_cart_order"].sample(20))

### ANALISE DE DADOS ###
print(df_orders["order_hour_of_day"].min(), df_orders["order_hour_of_day"].max())
print(df_orders["order_dow"].min(), df_orders["order_dow"].max())

# Quantas pessoas fazem pedidos a cada hora do dia?
people_per_hour = df_orders.groupby("order_hour_of_day")["user_id"].nunique()

people_per_hour.plot(
    kind="bar",
    title="Pessoas fazendo pedidos a cada hora do dia",
    color="hotpink",
    figsize=[8, 4],
    xlabel="Hora do dia",
    ylabel="Quantidade de pessoas",
)

day_of_week_orders = df_orders.groupby("order_dow")["user_id"].nunique()

# Em que dia da semana as pessoas compram produtos alimentícios?
day_of_week_orders.plot(
    kind="bar",
    title="Dia da semana que as pessoas mais fazem compras",
    color="hotpink",
    figsize=[8, 4],
    xlabel="Dias da semana",
    ylabel="Quantidade de pessoas",
)

# Quanto tempo as pessoas esperam até fazer outro pedido?
days_until_next_order = df_orders.groupby("days_since_prior_order")["user_id"].nunique()

days_until_next_order.plot(
    kind="bar",
    title="Quanto tempo as pessoas levam até seu próximo pedido",
    color="hotpink",
    figsize=[8, 4],
    xlabel="Dias até o próximo pedido",
    ylabel="Quantidade de pessoas",
)

# Diferenças nas quartas e sábados em 'order_hour_of_day'. Crie gráficos de barras para ambos os dias e descreva as diferenças.
# QUA
wed_orders = (
    df_orders[df_orders["order_dow"] == 3]
    .groupby("order_hour_of_day")["user_id"]
    .count()
)

wed_orders.plot(
    kind="bar",
    title="Pedidos na quarta-feira",
    color="tomato",
    xlabel="Horas do dia",
    ylabel="Quantidade de pedidos",
)

# SAB
sat_orders = (
    df_orders[df_orders["order_dow"] == 6]
    .groupby("order_hour_of_day")["user_id"]
    .count()
)

sat_orders.plot(
    kind="bar",
    title="Pedidos no Sábado",
    color="steelblue",
    xlabel="Horas do dia",
    ylabel="Quantidade de pedidos",
)

# SAB/QUA
diferences_between_sat_wed = (
    df_orders[df_orders["order_dow"].isin([3, 6])]
    .groupby("order_hour_of_day")["user_id"]
    .count()
)

diferences_between_sat_wed.plot(
    kind="bar",
    title="Diferença de pedidos entre as quartas-feiras e aos sábados",
    color=["tomato", "steelblue"],
    xlabel="Quarta/Sábado",
    ylabel="Quantidade de pedidos",
    rot=45,
)

# Qual é a distribuição do número de pedidos por cliente?
order_per_client = (
    df_orders.groupby("user_id")["order_id"].count().value_counts().sort_index()
)
order_per_client.plot(
    kind="bar",
    title="Numero de pedidos por cliente",
    xlabel="Numero de pedidos",
    ylabel="Quantidade de clientes",
    logy=True,
)

# Quais são os 20 produtos mais populares? Exiba os IDs e nomes.
merged_dfs = df_order_products.merge(
    df_products[["product_name", "product_id"]], on="product_id"
)

most_popular_itens_general = (
    merged_dfs.groupby(["product_name", "product_id"])["order_id"]
    .count()
    .sort_values(ascending=False)
    .head(20)
)

most_popular_itens_general.plot(
    kind="bar",
    title="20 Pedidos mais populares",
    color="gold",
    xlabel="Nome e ID dos produtos",
    ylabel="Quantidade de pedidos",
    rot=90,
)

# Quantos itens as pessoas normalmente compram em um pedido? Como fica a distribuição?
count_products_ordered = df_order_products.groupby("order_id")[
    "product_id"
].count()  # contagem dos produtos por cada ordem feita
count_products_ordered.plot(
    kind="hist",
    title="Mean Products per Orders",
    bins=range(count_products_ordered.max()),
    figsize=(10, 6),
    edgecolor="black",  # método não ensinada na lição, porém serve para adicionar uma borda da cor escolhida às barras do gráfico (aprendida após pesquisa)
    color="skyblue",  # alterar cor das barras do gráfico (aprendida após pesquisa) OBS: conjunto de cor 'black' com 'skyblue' foi uma indicação vista na internet e que fica com melhor forma de visualizar os dados
)

plt.xticks(
    range(0, 70, 5)
)  # método não ensinada na lição, porém serve para definir os valores de início e fim do eixo 'x' neste caso, bem como qual o tamanho de espaçamento nos valores que queremos que foi escolhido de 10 em 10 (aprendido após pesquisa)
plt.xlabel("Number of Items per Order")
plt.ylabel("Number of orders")
plt.show()

# Quais são os 20 principais itens incluídos com mais frequência em pedidos repetidos? Exiba os IDs e nomes.
merged_df = df_order_products.merge(
    df_products[["product_name", "product_id"]], on="product_id"
)
most_popular_itens = (
    merged_df[merged_df["reordered"] == 1]
    .groupby(["product_name", "product_id"])["order_id"]
    .count()
    .sort_values(ascending=False)
    .head(20)
)

most_popular_itens.plot(
    kind="bar",
    title="20 Produtos mais populares em pedidos repetidos",
    color="gold",
    xlabel="Nome e ID dos produtos",
    ylabel="Quantidade de pedidos",
    rot=90,
)

# Para cada produto, qual parcela de todos os pedidos dele são repetidos?
# Realiza a junção dos dataframes 'order_products' e 'products' com base em uma chave comum
df_merge = df_order_products.merge(df_products, on="product_id")

# Calcula a taxa de reordenação (média de 'reordered') para cada produto, agrupando pelo 'product_id' e 'product_name'
reorder_rate = df_merge.groupby(["product_id", "product_name"])["reordered"].mean()

# Exibe a taxa de reordenação calculada para cada produto
reorder_rate

# Para cada cliente, qual proporção de todos os seus pedidos são repetidos?
# Considera como "repetido" qualquer pedido com order_number > 1.
proporcao_pedidos_repetidos_cliente = (
    df_orders.groupby("user_id")["order_number"].apply(lambda s: (s > 1).mean())
)

# Criar uma tabela com as colunas de ID do cliente e a proporção de pedidos repetidos
tabela_proporcao_repetidos_cliente = (
    proporcao_pedidos_repetidos_cliente.reset_index()
    .rename(columns={"order_number": "proporcao_repetidos"})
)

# Exibir a tabela
print(tabela_proporcao_repetidos_cliente)

# Quais são os 20 principais itens que as pessoas colocam nos carrinhos antes de todos os outros?
top20_first = (
    merged_dfs[merged_dfs["add_to_cart_order"] == 1]
    .groupby(["product_id", "product_name"])["order_id"]
    .count()
    .sort_values(ascending=False)
    .head(20)
)

first_items = merged_dfs[merged_dfs["add_to_cart_order"] == 1]
top20_first = (
    first_items.groupby(["product_id", "product_name"])
    .size()
    .sort_values(ascending=False)
    .head(20)
)
top20_first.plot(
    kind="bar",
    title="20 Principais produtos colocados no carrinho primeiro",
    color="khaki",
    xlabel="Nome e ID dos produtos",
    ylabel="Numero de vezes que foi o primeiro item",
    rot=90,
)
