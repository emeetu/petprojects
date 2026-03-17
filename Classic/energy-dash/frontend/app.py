"""Streamlit UI: данные через FastAPI, таблица, графики, форма добавления, удаление по id."""
import os
import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")


def fetch_records(limit: int = 5000, offset: int = 0):
    try:
        r = requests.get(f"{API_BASE}/records", params={"limit": limit, "offset": offset}, timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка при загрузке данных: {e}")
        return None


def post_record(data: dict):
    try:
        r = requests.post(f"{API_BASE}/records", json=data, timeout=10)
        if r.status_code == 201:
            return True, "Запись успешно добавлена."
        if r.status_code == 422:
            detail = r.json().get("detail", [])
            errs = [f"{x.get('loc', [])}: {x.get('msg', '')}" for x in detail] if isinstance(detail, list) else [str(detail)]
            return False, "Ошибка валидации: " + "; ".join(errs)
        return False, f"Ошибка {r.status_code}: {r.text}"
    except requests.exceptions.RequestException as e:
        return False, str(e)


def delete_record(record_id: int):
    try:
        r = requests.delete(f"{API_BASE}/records/{record_id}", timeout=10)
        if r.status_code == 204:
            return True, "Запись удалена."
        if r.status_code == 404:
            return False, "Запись с указанным id не найдена."
        return False, f"Ошибка {r.status_code}: {r.text}"
    except requests.exceptions.RequestException as e:
        return False, str(e)


def main():
    st.set_page_config(page_title="Дашборд: энергопотребление и цены", layout="wide")
    st.title("Мини-дашборд: энергопотребление и цены (Европа / Сибирь)")

    with st.sidebar:
        st.header("Добавить запись")
        with st.form("add_record_form"):
            timestep = st.text_input("Время (timestep)", value="2011-11-23 12:00")
            consumption_eur = st.number_input("Потребление (Европа)", min_value=0.0, value=100000.0, step=1000.0)
            consumption_sib = st.number_input("Потребление (Сибирь)", min_value=0.0, value=25000.0, step=1000.0)
            price_eur = st.number_input("Цена (Европа)", min_value=0.0, value=900.0, step=10.0)
            price_sib = st.number_input("Цена (Сибирь)", min_value=0.0, value=550.0, step=10.0)
            submitted = st.form_submit_button("Добавить")
            if submitted:
                ok, msg = post_record({
                    "timestep": timestep,
                    "consumption_eur": consumption_eur,
                    "consumption_sib": consumption_sib,
                    "price_eur": price_eur,
                    "price_sib": price_sib,
                })
                (st.success if ok else st.error)(msg)
                if ok:
                    st.rerun()

        st.header("Удалить запись по id")
        del_id = st.number_input("ID записи", min_value=1, value=1, step=1, key="del_id")
        if st.button("Удалить"):
            ok, msg = delete_record(int(del_id))
            (st.success if ok else st.error)(msg)
            if ok:
                st.rerun()

    data = fetch_records()
    if data is None:
        st.warning("Не удалось загрузить данные. Убедитесь, что FastAPI запущен (uvicorn).")
        return

    df = pd.DataFrame(data)
    if df.empty:
        st.info("Нет записей.")
        return

    st.subheader("Таблица данных (с id)")
    st.dataframe(df, width="stretch", hide_index=True)

    st.subheader("Графики")
    n_show = min(500, len(df))
    df_plot = df.tail(n_show).copy()
    df_plot["timestep"] = pd.to_datetime(df_plot["timestep"], errors="coerce")

    col1, col2 = st.columns(2)
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_plot["timestep"], y=df_plot["consumption_eur"], name="Потребление (Европа)", mode="lines"))
        fig1.add_trace(go.Scatter(x=df_plot["timestep"], y=df_plot["consumption_sib"], name="Потребление (Сибирь)", mode="lines"))
        fig1.update_layout(title="Потребление энергии по времени", xaxis_title="Время", yaxis_title="Потребление", legend=dict(orientation="h"), height=350)
        st.plotly_chart(fig1, width="stretch")

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_plot["timestep"], y=df_plot["price_eur"], name="Цена (Европа)", mode="lines"))
        fig2.add_trace(go.Scatter(x=df_plot["timestep"], y=df_plot["price_sib"], name="Цена (Сибирь)", mode="lines"))
        fig2.update_layout(title="Цены по времени", xaxis_title="Время", yaxis_title="Цена", legend=dict(orientation="h"), height=350)
        st.plotly_chart(fig2, width="stretch")


if __name__ == "__main__":
    main()
