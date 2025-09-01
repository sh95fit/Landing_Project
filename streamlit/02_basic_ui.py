import streamlit as st
import pandas as pd
from datetime import datetime as dt
import datetime

# 버튼 클릭
button = st.button("버튼을 눌러보세요")

if button:
    st.write(":blue[버튼]을 누르셨습니다. :sparkles:")


# 파일 다운로드 버튼
# 샘플 데이터 생성
dataframe = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10,20,30,40],
})

# 다운로드 버튼 연결
st.download_button(
    label="Download CSV",
    data=dataframe.to_csv().encode("utf-8"),
    file_name=f"sample_data_{dt.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
)

# 체크 박스
agree = st.checkbox("동의하십니까?")

if agree:
    st.write(":blue[동의]하셨습니다. :100:")


# 라디오 선택 버튼
mbti = st.radio('당신의 MBTI는 무엇입니까?', ("ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"))

if mbti == 'ENFP':
    st.write("당신은 :green[활동가]입니다.")
elif mbti == 'ISTJ':
    st.write("당신은 :blue[현실주의자]입니다.")
else:
    st.write("당신은 :red[나만의 MBTI]입니다.")


# 단일 선택 박스
mbti = st.selectbox('당신의 MBTI는 무엇입니까?', ("ENFP", "ENTP", "ESTJ"), index=1)

if mbti == 'ENFP':
    st.write("당신은 :green[활동가]입니다.")
elif mbti == 'ENTP':
    st.write("당신은 :blue[현실주의자]입니다.")
else:
    st.write("당신은 :red[나만의 MBTI]입니다.")


# 다중 선택 박스
options = st.multiselect('당신의 관심사는 무엇입니까?', ("영화", "음악", "독서", "컴퓨터", "게임", "운동", "여행"))

st.write(f"당신의 선택은: :red[{options}]입니다.")


# 슬라이더
values = st.slider(
    '범위의 값을 다음과 같이 지정할 수 있어요 :sparkles:',
    0.0, 100.0, (25.0, 75.0),
)

st.write("선택 범위: ", values)


start_time = st.slider(
    "언제 약속을 잡는 것이 좋을까요?",
    min_value=dt(2020, 1, 1, 0, 0),
    max_value=dt(2020, 1, 7, 23, 0),
    value=dt(2020, 1, 3, 12, 0),
    step=datetime.timedelta(hours=1),
    format="MM/DD/YY - HH:mm"
)

st.write("선택한 약속 시간: ", start_time)


# 텍스트 입력
title = st.text_input(
    label="가고 싶은 여행지가 있나요?",
    placeholder="여행지를 입력해주세요."
)

st.write(f"선택한 여행지: :violet[{title}]")


# 숫자 입력
number = st.number_input(
    label="나이를 입력해 주세요.",
    min_value=10,
    max_value=100,
    value=30,
    step=1
)

st.write(f"선택한 나이: :orange[{number}]")