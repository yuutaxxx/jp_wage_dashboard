import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px

st.title("日本の賃金データ")

df_jp_industry = pd.read_csv("./data_csv/雇用_医療福祉_一人当たり賃金_全国_全産業.csv",encoding="shift-jis")
df_jp_category = pd.read_csv("./data_csv/雇用_医療福祉_一人当たり賃金_全国_大分類.csv",encoding="shift-jis")
df_pref_industry = pd.read_csv("./data_csv/雇用_医療福祉_一人当たり賃金_都道府県_全産業.csv",encoding="shift-jis")

pref_lat_lon = pd.read_csv("./data_csv/pref_lat_lon.csv")
pref_lat_lon = pref_lat_lon.rename(columns={"pref_name":"都道府県名"})
pref_lat_lon
df_pref_map = df_pref_industry[(df_pref_industry["年齢"] == "年齢計") & (df_pref_industry["集計年"] == 2019)]
df_pref_map = pd.merge(df_pref_map, pref_lat_lon, on="都道府県名")
df_pref_map["一人当たりの賃金（相対値）"] = (df_pref_map["一人当たり賃金（万円）"] - df_pref_map["一人当たり賃金（万円）"].min()) / (df_pref_map["一人当たり賃金（万円）"].max() - df_pref_map["一人当たり賃金（万円）"].min())

view = pdk.ViewState(
    longitude=140,
    latitude=36,
    zoom=5,
    pitch=60
)

layer = pdk.Layer(
    "HeatmapLayer",
    data=df_pref_map,
    opacity=0.4,
    get_position=["lon","lat"],
    threshold=0.3,
    get_weight = "一人当たりの賃金（相対値）"
)

layer_map = pdk.Deck(
    layers=layer,
    initial_view_state=view
)

st.pydeck_chart(layer_map)

show_df = st.checkbox("Show DataFrame")

if show_df:
    st.write(df_pref_map)

st.header("集計年別の一人当たりの賃金の推移")

df_pref_mean = df_pref_industry[df_pref_industry["年齢"] == "年齢計"]
pref_list = df_pref_mean["都道府県名"].unique()

option_pref = st.selectbox(
    "都道府県",
    pref_list
)

df_pref_mean = df_pref_mean[df_pref_mean["都道府県名"] == option_pref]
df_pref_mean

df_temp_mean = df_jp_industry[df_jp_industry["年齢"] == "年齢計"]
df_temp_mean = df_temp_mean.rename(columns={"一人当たり賃金（万円）":"全国＿一人当たり賃金（万円）"})

df_mean = pd.merge(df_temp_mean, df_pref_mean, on="集計年")
df_mean = df_mean[["集計年", "全国＿一人当たり賃金（万円）", "一人当たり賃金（万円）"]]
df_mean = df_mean.set_index("集計年")
st.line_chart(df_mean)

st.header("年齢別の全国＿一人当たり賃金")
df_jp_bubble = df_jp_industry[df_jp_industry["年齢"] != "年齢計"]
fig = px.scatter(df_jp_industry,
                 x="一人当たり賃金（万円）",
                 y="年間賞与その他特別給与額（万円）",
                 range_x=[150,700],
                 range_y=[0,150],
                 size="所定内給与額（万円）",
                 color="年齢",
                 animation_frame="集計年",
                 animation_group="年齢")

st.plotly_chart(fig)

st.header("◆産業別の賃金推移")
age_list = df_jp_category["集計年"].unique()
option_year = st.selectbox(
    "集計年",
    age_list)

wage_list = ["年間賞与その他特別給与額（万円）", "所定内給与額（万円）", "一人当たり賃金（万円）"]
option_wage = st.selectbox(
    "賃金の種類",
    wage_list
)

df_jp_mean = df_jp_category[df_jp_category["集計年"] == option_year]

max_x = df_jp_mean[option_wage].max() + 50 #50マージン用

fig = px.bar(df_jp_mean,
             x=option_wage,
             y="産業大分類名",
             color="産業大分類名",
             animation_frame="年齢",
             range_x=[0,max_x],
             orientation="h",
             width=800,
             height=500)

st.plotly_chart(fig)

