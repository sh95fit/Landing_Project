import streamlit as st

#  타이틀 적용 예시
st.title("This is a title")

# 특수 이모티콘 삽입 예시
# emoji : https://streamlit-emoji-shortcodes-streamlit-app-gwckqd.streamlitapp.com/
st.title('smile :sunglasses:')

# Header 적용 예시
st.header("Header :sparkles")

# Subheader 적용 예시
st.subheader("This is a subheader")

# 캡션 적용 예시
st.caption("This is a caption")

# 코드 표시
sample_code = '''
def function():
    print("Hello, World!")
'''
st.code(sample_code, language="python")

# 일반 텍스트
st.text("This is a text")

# 마크다운 문법 적용 예시
st.markdown('streamlit은 **마크다운 문법을 지원**합니다.')

# 컬러코드 : blue, green, orange, red, purple, violet
st.markdown("텍스트 색상을 :green[초록색]으로, 그리고 **:blue[파란색]** 으로 표시할 수 있습니다.")
st.markdown(":green[$\sqrt{x^2+y^2}=1$]와 같이 latex 문법을 사용할 수 있습니다.")

# LaTex 수식 지원
st.latex(r'\sqrt{x^2+y^2}=1')