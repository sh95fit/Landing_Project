import streamlit as st
import pandas as pd
import numpy as np

st.title('DataFrame Tutorial')

# DataFrame 생성
dataframe = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [5, 6, 7, 8],
    'third column': [9, 10, 11, 12]
})

# DataFrame 출력
# use_container_width 기능은 데이터프레임을 컨테이너 크기에 맞게 확장할 때 사용
st.write(dataframe, use_container_width=False)

# Table (static)
# DataFrame과 다르게 interactive한 UI를 제공하지 않음
st.table(dataframe)


# 메트릭
st.metric(label="삼성전자", value="80,000 원", delta="-1,200원")
st.metric(label="카카오", value="50,000 원", delta="2,000원")


# 컬럼으로 영역을 나누어 표기한 경우
col1, col2, col3 = st.columns(3)
col1.metric(label="삼성전자", value="80,000 원", delta="-1,200원")
col2.metric(label="카카오", value="50,000 원", delta="2,000원")
col3.metric(label="네이버", value="300,000 원", delta="1,000원")