import streamlit as st
import pandas as pd
import numpy as np
from streamlit_extras.chart_container import chart_container

st.set_page_config(
    page_title="Auto Landing Page",
    page_icon="📊",
    initial_sidebar_state="collapsed",
    layout="wide",
    menu_items={
        'Get Help': None,
        # 'Report a bug': None,
        # 'About': None
    },
)

with st.sidebar:
    st.write("Sidebar")



col1, col2 = st.columns([1,3])

with col1:
    st.title("Auto Landing Page")
    st.write("This is a landing page for a product or service.")
    st.markdown("**Landing Page**")
    
with col2:
    test2 = [1,2,3,4,5]
    st.write(test2)


    @st.cache_data
    def get_data():
        df = pd.DataFrame(
            np.random.randn(50, 20), columns=("col %d" % i for i in range(20))
        )
        return df

    @st.cache_data
    def convert_for_download(df):
        return df.to_csv().encode("utf-8")

    df = get_data()
    csv = convert_for_download(df)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="data.csv",
        mime="text/csv",
        icon=":material/download:",
    )

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write(df)