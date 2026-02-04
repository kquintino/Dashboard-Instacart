from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Instacart Dashboard", layout="wide")

BASE_DIR = Path(__file__).resolve().parent


@st.cache_data
def load_data():
    df_orders = pd.read_csv(
        BASE_DIR / "orders.csv",
        sep=";",
        usecols=["order_id", "user_id", "order_dow", "order_hour_of_day"],
        dtype={
            "order_id": "int32",
            "user_id": "int32",
            "order_dow": "int8",
            "order_hour_of_day": "int8",
        },
    )
    df_products = pd.read_csv(
        BASE_DIR / "products.csv",
        sep=";",
        usecols=["product_id", "product_name", "department_id"],
        dtype={"product_id": "int32", "department_id": "int16"},
    )
    df_products["product_name"] = df_products["product_name"].astype("category")
    df_departments = pd.read_csv(
        BASE_DIR / "departments.csv",
        sep=";",
        usecols=["department_id", "department"],
        dtype={"department_id": "int16"},
    )
    df_departments["department"] = df_departments["department"].astype("category")
    return df_orders, df_products, df_departments


@st.cache_data
def load_order_products_aggregates(chunksize=1_000_000):
    product_counts = None
    order_counts = None
    for chunk in pd.read_csv(
        BASE_DIR / "order_products.csv",
        sep=";",
        usecols=["order_id", "product_id"],
        dtype={"order_id": "int32", "product_id": "int32"},
        chunksize=chunksize,
    ):
        chunk_product_counts = chunk["product_id"].value_counts()
        if product_counts is None:
            product_counts = chunk_product_counts
        else:
            product_counts = product_counts.add(chunk_product_counts, fill_value=0)

        chunk_order_counts = chunk["order_id"].value_counts()
        if order_counts is None:
            order_counts = chunk_order_counts
        else:
            order_counts = order_counts.add(chunk_order_counts, fill_value=0)

    product_counts = product_counts.astype("int64").rename_axis("product_id")
    order_counts = order_counts.astype("int64").rename_axis("order_id")
    return product_counts, order_counts


df_orders, df_products, df_departments = load_data()
product_counts, order_counts = load_order_products_aggregates()

day_names = {
    0: "Domingo",
    1: "Segunda",
    2: "Terça",
    3: "Quarta",
    4: "Quinta",
    5: "Sexta",
    6: "Sábado",
}

hour_labels = [
    f"{h:2d}am" if h < 12 else ("12pm" if h == 12 else f"{h-12:2d}pm")
    for h in range(24)
]

st.title("Instacart Dashboard")

st.header("Heatmap: pedidos por dia e hora")
heatmap_df = (
    df_orders.groupby(["order_dow", "order_hour_of_day"])["order_id"]
    .count()
    .reset_index(name="order_count")
)
heatmap_df["day_name"] = heatmap_df["order_dow"].map(day_names)
heatmap_df["hour_label"] = heatmap_df["order_hour_of_day"].map(
    dict(enumerate(hour_labels))
)
fig = px.density_heatmap(
    heatmap_df,
    x="hour_label",
    y="day_name",
    z="order_count",
    color_continuous_scale="Reds",
    title="Heatmap de pedidos por dia e hora",
    labels={
        "day_name": "Dias da semana",
        "hour_label": "Horas do dia",
        "order_count": "Escala por volume",
    },
    category_orders={"day_name": [day_names[i] for i in range(7)]},
)
fig.update_layout(xaxis_tickangle=90, coloraxis_colorbar={"title": "Escala por volume"})
st.plotly_chart(fig, width="stretch")

st.header("Pedidos por hora (todos os dias da semana)")
orders_by_hour_all = (
    df_orders.groupby(["order_dow", "order_hour_of_day"])["user_id"]
    .count()
    .reset_index(name="order_count")
)
orders_by_hour_all["hour_label"] = orders_by_hour_all["order_hour_of_day"].map(
    dict(enumerate(hour_labels))
)
fig = go.Figure()
for dow in range(7):
    data = orders_by_hour_all[orders_by_hour_all["order_dow"] == dow]
    fig.add_bar(
        x=data["hour_label"],
        y=data["order_count"],
        name=day_names[dow],
        visible=(dow == 0),
    )

buttons = []
for i in range(7):
    visibility = [False] * 7
    visibility[i] = True
    buttons.append(
        dict(
            label=day_names[i],
            method="update",
            args=[
                {"visible": visibility},
                {"title": f"Pedidos por hora - {day_names[i]}"},
            ],
        )
    )

fig.update_layout(
    title=f"Pedidos por hora - {day_names[0]}",
    xaxis_title="Horas do dia",
    yaxis_title="Quantidade de pedidos",
    xaxis_tickangle=90,
    height=450,
    margin={"l": 40, "r": 20, "t": 60, "b": 60},
    updatemenus=[
        dict(
            active=0,
            buttons=buttons,
            x=1.0,
            xanchor="right",
            y=1.15,
            yanchor="top",
        )
    ],
)
st.plotly_chart(fig, width="stretch")

st.header("Comparacao de volume por hora (2 dias da semana)")
selected_days = st.multiselect(
    "Selecione dois dias para comparar",
    options=list(day_names.keys()),
    default=[0, 1],
    format_func=lambda d: day_names[d],
)
if len(selected_days) != 2:
    st.info("Selecione exatamente 2 dias para comparar.")
else:
    fig = go.Figure()
    for dow in selected_days:
        data = orders_by_hour_all[orders_by_hour_all["order_dow"] == dow]
        fig.add_bar(
            x=data["hour_label"],
            y=data["order_count"],
            name=day_names[dow],
            opacity=0.7,
        )
    fig.update_layout(
        barmode="overlay",
        title=f"Comparacao de volume por hora - {day_names[selected_days[0]]} vs {day_names[selected_days[1]]}",
        xaxis_title="Horas do dia",
        yaxis_title="Quantidade de pedidos",
        xaxis_tickangle=90,
    )
    st.plotly_chart(fig, width="stretch")

st.header("20 pedidos mais populares")
product_counts_df = product_counts.rename("order_count").reset_index()
most_popular_itens_general = (
    product_counts_df.merge(
        df_products[["product_id", "product_name"]], on="product_id"
    )
    .sort_values("order_count", ascending=False)
    .head(20)
    .reset_index(drop=True)
)
most_popular_itens_general["product_label"] = (
    most_popular_itens_general["product_name"]
    + " ("
    + most_popular_itens_general["product_id"].astype(str)
    + ")"
)
fig = px.bar(
    most_popular_itens_general,
    x="product_label",
    y="order_count",
    labels={
        "product_label": "Nome e ID dos produtos",
        "order_count": "Quantidade de pedidos",
    },
    color_discrete_sequence=["gold"],
)
fig.update_layout(xaxis_tickangle=90)
st.plotly_chart(fig, width="stretch")

st.header("Top 20 produtos por departamento")
prod_dept = product_counts_df.merge(
    df_products[["product_id", "product_name", "department_id"]], on="product_id"
).merge(df_departments[["department_id", "department"]], on="department_id")
top_prod_dept = (
    prod_dept.groupby(["department", "product_name"])["order_count"]
    .sum()
    .reset_index()
)
top_prod_dept = (
    top_prod_dept.sort_values(["department", "order_count"], ascending=[True, False])
    .groupby("department")
    .head(20)
)
fig = px.scatter(
    top_prod_dept,
    x="department",
    y="order_count",
    size="order_count",
    color="department",
    hover_name="product_name",
    labels={
        "department": "Departamento",
        "order_count": "Quantidade de pedidos",
    },
)
fig.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig, width="stretch")

st.header("Distribuicao de itens por pedido")
count_products_ordered = order_counts
max_x = int(count_products_ordered.quantile(0.99))
count_products_df = (
    count_products_ordered[count_products_ordered <= max_x]
    .to_frame(name="items_per_order")
    .reset_index(drop=True)
)
fig = px.histogram(
    count_products_df,
    x="items_per_order",
    nbins=max_x,
    title="Distribuicao de itens por pedido (ate 99%)",
    labels={"items_per_order": "Itens por pedido", "count": "Numero de pedidos"},
    color_discrete_sequence=["skyblue"],
)
fig.update_traces(marker_line_color="black", marker_line_width=1)
fig.update_layout(xaxis_range=[0.5, max_x + 0.5])
st.plotly_chart(fig, width="stretch")
