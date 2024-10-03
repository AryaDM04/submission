import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data_path = "all_data.csv"
all_data = pd.read_csv(data_path)
all_data["order_purchase_timestamp"] = pd.to_datetime(
    all_data["order_purchase_timestamp"]
)

st.sidebar.image("Logo.png", width=100)


st.image("Logo.png", width=50)
st.title("Dashboard Analisis Data Penjualan E-commerce")

st.markdown("## Visualisasi & Analisis Penjelasan")

st.sidebar.header("Filter Data")
years_filter = st.sidebar.multiselect(
    "Pilih Tahun:", options=[2016, 2017, 2018], default=[2018]
)
years_filter.sort()

option = st.sidebar.selectbox(
    "Pilih Visualisasi:",
    (
        "Tren Kepuasan Pelanggan",
        "Total Pengeluaran Tertinggi",
        "10 Barang Paling dan Tidak Laris",
    ),
)

data_filtered = all_data[
    all_data["order_purchase_timestamp"].dt.year.isin(years_filter)
]
if not years_filter:
    st.sidebar.warning("Silakan pilih tahun untuk melanjutkan analisis.")
    st.stop()


def display_conclusion(option, data):
    if option == "Tren Kepuasan Pelanggan":
        monthly_review_trend = data.copy()
        monthly_review_trend["year_month"] = monthly_review_trend[
            "order_purchase_timestamp"
        ].dt.to_period("M")
        monthly_review_trend = (
            monthly_review_trend.groupby("year_month")["review_score"]
            .mean()
            .reset_index()
        )

        max_score = monthly_review_trend["review_score"].max()
        min_score = monthly_review_trend["review_score"].min()
        max_month = monthly_review_trend.loc[
            monthly_review_trend["review_score"].idxmax(), "year_month"
        ].to_timestamp()
        min_month = monthly_review_trend.loc[
            monthly_review_trend["review_score"].idxmin(), "year_month"
        ].to_timestamp()

        conclusion = (
            f"### Kesimpulan Tren Kepuasan Pelanggan ({', '.join(map(str, years_filter))}):\n"
            f"- Skor ulasan tertinggi tercatat pada {max_month.strftime('%B %Y')} dengan nilai {max_score:.2f}.\n"
            f"- Sebaliknya, skor ulasan terendah tercatat pada {min_month.strftime('%B %Y')} dengan nilai {min_score:.2f}.\n"
        )

    elif option == "Total Pengeluaran Tertinggi":
        total_spending_per_city = (
            data.groupby("customer_city")["payment_value"].sum().reset_index()
        )
        highest_city = total_spending_per_city.loc[
            total_spending_per_city["payment_value"].idxmax()
        ]
        second_city = total_spending_per_city.nlargest(2, "payment_value").iloc[1]

        conclusion = (
            f"### Kesimpulan Pengeluaran Tertinggi oleh Wilayah ({', '.join(map(str, years_filter))}):\n"
            f"- Wilayah **{highest_city['customer_city']}** menjadi kota dengan total pengeluaran tertinggi, mencapai sekitar **{highest_city['payment_value']:.2f}** USD, diikuti oleh **{second_city['customer_city']}** dengan pengeluaran sekitar **{second_city['payment_value']:.2f}** USD.\n"
            "- Ini menunjukkan bahwa pelanggan di wilayah metropolitan besar memiliki daya beli yang lebih tinggi."
        )

    elif option == "10 Barang Paling dan Tidak Laris":
        sum_order_items_df = (
            data.groupby("product_category_name_english")["product_id"]
            .count()
            .reset_index()
        )
        top_10_best_selling = sum_order_items_df.nlargest(10, "product_id")
        bottom_10_least_selling = sum_order_items_df.nsmallest(10, "product_id")

        conclusion = (
            f"### Kesimpulan Barang Paling dan Tidak Laris ({', '.join(map(str, years_filter))}):\n"
            f"- Produk terlaris didominasi oleh kategori kebutuhan sehari-hari, dengan total penjualan mencapai **{top_10_best_selling['product_id'].sum():,}** unit.\n"
            f"- Sebaliknya, produk dengan penjualan terendah menunjukkan bahwa ada kategori yang kurang diminati, dengan penjualan di bawah **{bottom_10_least_selling['product_id'].min():,}** unit."
        )

    return conclusion


if option == "Tren Kepuasan Pelanggan":
    st.subheader(
        f"Tren Kepuasan Pelanggan Berdasarkan Skor Ulasan ({', '.join(map(str, years_filter))})"
    )
    monthly_review_trend = data_filtered.copy()
    monthly_review_trend["year_month"] = monthly_review_trend[
        "order_purchase_timestamp"
    ].dt.to_period("M")
    monthly_review_trend = (
        monthly_review_trend.groupby("year_month")["review_score"].mean().reset_index()
    )
    monthly_review_trend["year_month"] = monthly_review_trend[
        "year_month"
    ].dt.to_timestamp()

    plt.figure(figsize=(14, 6))
    sns.lineplot(
        data=monthly_review_trend,
        x="year_month",
        y="review_score",
        marker="o",
        color="b",
        markersize=8,
    )
    plt.axhline(
        y=monthly_review_trend["review_score"].mean(),
        color="r",
        linestyle="--",
        label="Rata-rata Skor Ulasan",
    )
    plt.title("Tren Kepuasan Pelanggan (Skor Ulasan) 2016-2018")
    plt.xlabel("Tanggal")
    plt.ylabel("Rata-rata Skor Ulasan")
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend()
    st.pyplot(plt)
    st.write(display_conclusion(option, data_filtered))

elif option == "Total Pengeluaran Tertinggi":
    st.subheader(f"Total Pengeluaran Tertinggi ({', '.join(map(str, years_filter))})")
    total_spending_per_city = (
        data_filtered.groupby("customer_city")["payment_value"].sum().reset_index()
    )
    total_spending_per_city = total_spending_per_city.rename(
        columns={"payment_value": "total_spending"}
    )
    top_cities_spending = total_spending_per_city.sort_values(
        by="total_spending", ascending=False
    ).head(10)

    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=top_cities_spending,
        x="customer_city",
        y="total_spending",
        palette="viridis",
    )
    plt.title("10 Kota dengan Total Pengeluaran Tertinggi")
    plt.xlabel("Kota")
    plt.ylabel("Total Pengeluaran")
    plt.xticks(rotation=45)
    plt.grid(axis="y")
    st.pyplot(plt)
    st.write(display_conclusion(option, data_filtered))

elif option == "10 Barang Paling dan Tidak Laris":
    st.subheader(
        f"10 Barang Paling dan Tidak Laris ({', '.join(map(str, years_filter))})"
    )
    sum_order_items_df = (
        data_filtered.groupby("product_category_name_english")["product_id"]
        .count()
        .reset_index()
    )
    sum_order_items_df = sum_order_items_df.rename(columns={"product_id": "products"})
    sum_order_items_df = sum_order_items_df.sort_values(by="products", ascending=False)

    top_10_best_selling = sum_order_items_df.head(10)
    bottom_10_least_selling = sum_order_items_df.tail(10)

    fig, ax = plt.subplots(2, 1, figsize=(12, 10))
    sns.barplot(
        x="products",
        y="product_category_name_english",
        data=top_10_best_selling,
        ax=ax[0],
        palette="viridis",
    )
    ax[0].set_title("10 Barang Terlaris")
    ax[0].set_xlabel("Jumlah Produk Terjual")
    ax[0].set_ylabel("Kategori Produk")

    sns.barplot(
        x="products",
        y="product_category_name_english",
        data=bottom_10_least_selling,
        ax=ax[1],
        palette="plasma",
    )
    ax[1].set_title("10 Barang Tidak Terlaris")
    ax[1].set_xlabel("Jumlah Produk Terjual")
    ax[1].set_ylabel("Kategori Produk")

    plt.tight_layout()
    st.pyplot(fig)
    st.write(display_conclusion(option, data_filtered))
