import streamlit as st
import pandas as pd
import plotly.express as px
from utils import detect_and_normalize, build_report
from io import BytesIO

st.set_page_config(page_title='Маркетплейс — Аналитика', layout='wide')
st.title('Визуальный бизнес-отчёт по маркетплейсам')
st.caption('Загрузите отчёт Ozon или Wildberries (.xlsx). Приложение автоматически распознает формат и сформирует интерактивный дашборд.')

# Sidebar: загрузка
with st.sidebar:
    st.header('Загрузка')
    uploaded_file = st.file_uploader('Выберите Excel файл', type=['xlsx','xls'])
    st.write('Или используйте примеры (локальные пути):')
    st.code('/mnt/data/озон.xlsx')
    st.code('/mnt/data/вб.xlsx')
    st.markdown('---')
    st.caption('Совет: для локальной разработки используйте кнопки ниже, если эти файлы существуют в окружении.')
    if st.button('Загрузить локальный пример Ozon'):
        try:
            uploaded_file = '/mnt/data/озон.xlsx'
        except Exception:
            st.sidebar.error('Локальный пример недоступен.')

@st.cache_data
def read_excel(uploaded):
    if uploaded is None:
        return None
    try:
        if isinstance(uploaded, str):
            # path provided
            df = pd.read_excel(uploaded, engine='openpyxl')
        else:
            df = pd.read_excel(uploaded, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f'Ошибка чтения файла: {e}')
        return None

df = read_excel(uploaded_file)

if df is not None:
    st.success('Файл загружен — выполняется распознавание и нормализация...')
    detected = detect_and_normalize(df)  # returns dict with 'rows', 'marketplace', 'mapping'
    report = build_report(detected['rows'])

    # KPI
    k1, k2, k3, k4 = st.columns(4)
    k1.metric('Оборот', f\"{report['aggregates']['turnover']:,}\")
    k2.metric('Чистая прибыль', f\"{report['profit']:,}\")
    k3.metric('Комиссия', f\"{report['aggregates']['commission']:,}\")
    k4.metric('Логистика', f\"{report['aggregates']['logistics']:,}\")

    st.markdown('---')

    # Time series (if any)
    if report['series']:
        fig_time = px.line(report['series'], x='date', y='turnover', title='Динамика оборота')
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info('В файле нет распознанных дат — динамика недоступна.')

    # Pie chart: cost structure
    fig_pie = px.pie(names=[p['name'] for p in report['chart']], values=[p['value'] for p in report['chart']], title='Структура расходов')
    st.plotly_chart(fig_pie, use_container_width=True)

    # Top brands & categories
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader('Топ брендов')
        if report['topBrands']:
            st.table(pd.DataFrame(report['topBrands']).head(10))
        else:
            st.info('Нет данных по брендам')

    with col_b:
        st.subheader('Топ категорий')
        if report['topCats']:
            st.table(pd.DataFrame(report['topCats']).head(10))
        else:
            st.info('Нет данных по категориям')

    st.markdown('---')

    # Raw rows preview
    st.subheader('Первые 50 строк (нормализованные)')
    st.dataframe(pd.DataFrame(report['rows']).head(50))

    # Export XLSX
    def to_excel_bytes(report_obj):
        out = BytesIO()
        writer = pd.ExcelWriter(out, engine='openpyxl')
        pd.DataFrame(report_obj['rows']).to_excel(writer, sheet_name='rows', index=False)
        agg = pd.DataFrame([report_obj['aggregates']])
        agg['profit'] = report_obj['profit']
        agg.to_excel(writer, sheet_name='aggregates', index=False)
        writer.save()
        return out.getvalue()

    if st.button('Скачать отчёт в Excel'):
        x = to_excel_bytes(report)
        st.download_button('Скачать отчёт (XLSX)', data=x, file_name='marketplace_report.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

else:
    st.info('Загрузите файл Excel в левом меню, чтобы начать анализ.')
