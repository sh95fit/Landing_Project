import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
from dotenv import load_dotenv

load_dotenv()

ALPHAVANTAGE_API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')

end_date = datetime.now().date()
# start_date = end_date - timedelta(days=1)
start_date = end_date - relativedelta(years=1)

st.title('Stock Dashboard')
ticker = st.sidebar.text_input('Ticker', 'AAPL')
start_date = st.sidebar.date_input("Start Date", value=start_date)
end_date = st.sidebar.date_input("End Date", value=end_date)

# 데이터 다운로드 및 처리 
try:
    # auto_adjust=True를 사용하면 Close 컬럼이 이미 조정된 가격이 됩니다
    # auto_adjust=False를 사용하면 Adj Close 컬럼을 별도로 받을 수 있습니다
    use_adjusted = st.sidebar.checkbox('Use Adjusted Prices', value=True)
    
    if use_adjusted:
        # 조정된 가격 사용 (Close 컬럼이 조정된 가격)
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True, group_by='ticker')
        price_column = 'Close'
    else:
        # 원본 가격 및 조정 가격 둘 다 받기
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, group_by='ticker')
        price_column = st.sidebar.selectbox('Price Type', ['Close', 'Adj Close'], index=1)
    
    # MultiIndex 컬럼 문제 해결
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(0)  # ticker 레벨 제거
    
    # 컬럼명 정리
    data.columns = [col.strip() for col in data.columns]
    
    # st.sidebar.write(f"Available columns: {list(data.columns)}")
    
except Exception as e:
    st.error(f"Error downloading data: {e}")
    data = pd.DataFrame()


# 데이터가 비어있지 않은지 확인
if not data.empty:
    # 인덱스를 리셋하여 Date를 컬럼으로 만들기
    data_reset = data.reset_index()
    
    fig = px.line(data_reset, x='Date', y=price_column, title=f'{ticker} Stock Price ({price_column})')
    st.plotly_chart(fig)
    
    # 추가 정보 표시
    st.subheader('Recent Data')
    st.dataframe(data.tail())
    
    st.subheader('Statistics')
    st.write(data[price_column].describe())
else:
    st.error("No data found for the given ticker and date range.")


pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

with pricing_data :
    st.header('Pricing Movements')
    data2 = data.copy()

    # 사용할 가격 컬럼 결정 
    if 'Adj Close' in data.columns:
        price_col = 'Adj Close'
        st.info("📊 Using Adjusted Close prices for calculations")
    elif 'Close' in data.columns:
        price_col = 'Close'
        st.info("📊 Using Close prices for calculations")
    else:
        st.error("❌ No suitable price column found!")
        st.stop()

    data2['% Change'] = data[price_col] / data[price_col].shift(1) - 1
    data2.dropna(inplace=True)
    st.write(data2)
    annual_return = data2['% Change'].mean() * 252 * 100
    st.write('Annual Return is ', annual_return, '%')
    stdev = np.std(data2['% Change'])*np.sqrt(252)
    st.write('Standard Deviation is ', stdev*100, '%')
    st.write('Risk Adj. Return is ', annual_return/(stdev*100))

with fundamental_data :
    api_key = ALPHAVANTAGE_API_KEY

    if not api_key:
        st.error("❌ Alpha Vantage API key not found!")
        st.write("**Setup Instructions:**")
        st.write("1. Create a `.env` file in your project root")
        st.write("2. Add this line to the `.env` file:")
        st.code("ALPHA_VANTAGE_API_KEY=your_api_key_here", language="bash")
        st.write("3. Get your free API key from https://www.alphavantage.co/support/#api-key")
        st.write("4. Install python-dotenv:")
        st.code("pip install python-dotenv", language="bash")
        
        # 대체 옵션으로 수동 입력도 제공
        st.write("---")
        st.write("**Alternative: Manual Input**")
        manual_key = st.text_input("Enter API Key manually", 
                                type="password",
                                help="This will only be used for this session")
        if manual_key:
            api_key = manual_key

    if api_key:
        try:
            from alpha_vantage.fundamentaldata import FundamentalData
                        # API 키 상태 표시 (마스킹)
            masked_key = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:] if len(api_key) > 12 else "*" * len(api_key)
            st.success(f"🔑 API Key loaded: {masked_key}")

            fd = FundamentalData(api_key, output_format='pandas')

            @st.cache_data(ttl=3600) # 1시간 캐시
            def get_financial_data(ticker, api_key) :
                fd = FundamentalData(api_key, output_format='pandas')
                try:
                    balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
                    income_statement = fd.get_income_statement_annual(ticker)[0]
                    cash_flow = fd.get_cash_flow_annual(ticker)[0]
                    return balance_sheet, income_statement, cash_flow, None
                except Exception as e:
                    return None, None, None, str(e)
                
            # 데이터 로드
            with st.spinner('Loading financial data...'):
                balance_sheet, income_statement, cash_flow, error = get_financial_data(ticker, api_key)  

            if error:
                st.error(f"❌ Error: {error}")
                st.info("💡 Possible issues:")
                st.write("- Invalid ticker symbol")
                st.write("- API key quota exceeded (25 calls/day for free)")
                st.write("- Network connection problem")
                st.write("- Invalid API key")
            else:
                # Balance Sheet
                if balance_sheet is not None and not balance_sheet.empty:
                    st.subheader('📊 Balance Sheet (Annual)')
                    try:
                        bs = balance_sheet.T[2:]
                        bs.columns = list(balance_sheet.T.iloc[0])
                        
                        # 숫자 형식 개선
                        numeric_columns = bs.select_dtypes(include=['number']).columns
                        for col in numeric_columns:
                            bs[col] = bs[col].apply(lambda x: f"${x/1e9:.2f}B" if abs(x) >= 1e9 else f"${x/1e6:.2f}M" if abs(x) >= 1e6 else f"${x:,.0f}")
                        
                        st.dataframe(bs, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error processing balance sheet: {e}")

                # Income Statement
                if income_statement is not None and not income_statement.empty:
                    st.subheader('💰 Income Statement (Annual)')
                    try:
                        is1 = income_statement.T[2:]
                        is1.columns = list(income_statement.T.iloc[0])
                        
                        # 숫자 형식 개선
                        numeric_columns = is1.select_dtypes(include=['number']).columns
                        for col in numeric_columns:
                            is1[col] = is1[col].apply(lambda x: f"${x/1e9:.2f}B" if abs(x) >= 1e9 else f"${x/1e6:.2f}M" if abs(x) >= 1e6 else f"${x:,.0f}")
                        
                        st.dataframe(is1, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error processing income statement: {e}")
                
                # Cash Flow Statement
                if cash_flow is not None and not cash_flow.empty:
                    st.subheader('💸 Cash Flow Statement (Annual)')
                    try:
                        cf = cash_flow.T[2:]
                        cf.columns = list(cash_flow.T.iloc[0])
                        
                        # 숫자 형식 개선
                        numeric_columns = cf.select_dtypes(include=['number']).columns
                        for col in numeric_columns:
                            cf[col] = cf[col].apply(lambda x: f"${x/1e9:.2f}B" if abs(x) >= 1e9 else f"${x/1e6:.2f}M" if abs(x) >= 1e6 else f"${x:,.0f}")
                        
                        st.dataframe(cf, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error processing cash flow: {e}")
                
                st.success("✅ Financial data loaded successfully!")
                st.info("🔄 Data is cached for 1 hour to save API calls")
                
        except ImportError:
            st.error("❌ Required packages not installed!")
            st.code("pip install alpha-vantage python-dotenv", language="bash")
            
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

with news:
    st.header(f'📰 Latest News for {ticker}')
    
    try:
        from stocknews import StockNews
        
        with st.spinner('Loading latest news...'):
            sn = StockNews(ticker, save_news=False)
            df_news = sn.read_rss()
        
        if df_news is not None and not df_news.empty:
            # 뉴스 개수 확인 (최대 10개)
            news_count = min(10, len(df_news))
            st.success(f"✅ Found {news_count} news articles")
            
            # 감정 분석 색상 함수
            def get_sentiment_color(sentiment):
                # numpy 타입을 문자열로 안전하게 변환
                sentiment_str = str(sentiment).lower() if sentiment is not None else 'neutral'
                
                if 'positive' in sentiment_str or sentiment_str == '1' or sentiment_str == '1.0':
                    return '🟢', '#28a745'
                elif 'negative' in sentiment_str or sentiment_str == '-1' or sentiment_str == '-1.0':
                    return '🔴', '#dc3545'
                else:
                    return '🟡', '#ffc107'
            
            def safe_capitalize(value):
                """안전하게 문자열로 변환하고 첫 글자를 대문자로"""
                if value is None:
                    return 'N/A'
                
                str_value = str(value).lower()
                
                # 숫자 값을 감정으로 변환
                if str_value == '1' or str_value == '1.0':
                    return 'Positive'
                elif str_value == '-1' or str_value == '-1.0':
                    return 'Negative'
                elif str_value == '0' or str_value == '0.0':
                    return 'Neutral'
                else:
                    return str_value.capitalize()
            
            # 뉴스 카드 스타일
            for i in range(news_count):
                try:
                    # 뉴스 데이터 추출 (안전하게 처리)
                    published = str(df_news['published'].iloc[i]) if 'published' in df_news.columns else 'N/A'
                    title = str(df_news['title'].iloc[i]) if 'title' in df_news.columns else 'No Title'
                    summary = str(df_news['summary'].iloc[i]) if 'summary' in df_news.columns else 'No Summary'
                    title_sentiment = df_news['sentiment_title'].iloc[i] if 'sentiment_title' in df_news.columns else 'neutral'
                    summary_sentiment = df_news['sentiment_summary'].iloc[i] if 'sentiment_summary' in df_news.columns else 'neutral'
                    
                    # 감정 분석 아이콘과 색상 (안전하게 처리)
                    title_icon, title_color = get_sentiment_color(title_sentiment)
                    summary_icon, summary_color = get_sentiment_color(summary_sentiment)
                    
                    # 감정 텍스트 안전하게 변환
                    title_sentiment_text = safe_capitalize(title_sentiment)
                    summary_sentiment_text = safe_capitalize(summary_sentiment)
                    
                    # 뉴스 카드 생성
                    with st.container():
                        # 카드 헤더
                        st.markdown(f"""
                        <div style="
                            background-color: #f8f9fa;
                            border-left: 4px solid #007bff;
                            padding: 1rem;
                            margin: 1rem 0;
                            border-radius: 0.5rem;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        ">
                        <h4 style="margin: 0 0 0.5rem 0; color: #333;">📰 News #{i+1}</h4>
                        <p style="margin: 0; color: #666; font-size: 0.9rem;">📅 {published}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 제목과 요약을 컬럼으로 배치
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**📄 Title:** {title}")
                            st.markdown(f"**📝 Summary:** {summary}")
                        
                        with col2:
                            st.markdown("**🎭 Sentiment Analysis**")
                            st.markdown(f"{title_icon} **Title:** {title_sentiment_text}")
                            st.markdown(f"{summary_icon} **Summary:** {summary_sentiment_text}")
                            
                            # 디버그 정보 (개발 중에만 표시)
                            if st.checkbox(f"Show debug info #{i+1}", key=f"debug_{i}"):
                                st.write(f"Raw title sentiment: {title_sentiment} (type: {type(title_sentiment)})")
                                st.write(f"Raw summary sentiment: {summary_sentiment} (type: {type(summary_sentiment)})")
                        
                        # 구분선
                        st.divider()
                        
                except Exception as e:
                    st.error(f"Error displaying news #{i+1}: {str(e)}")
                    continue
            
            # 전체 감정 분석 요약 (안전하게 처리)
            if news_count > 0:
                st.subheader("📊 Overall Sentiment Analysis")
                
                try:
                    # 감정 분석 통계 (numpy 타입 안전하게 처리)
                    if 'sentiment_title' in df_news.columns:
                        title_sentiments = df_news['sentiment_title'].head(news_count).apply(safe_capitalize).value_counts()
                    else:
                        title_sentiments = {}
                        
                    if 'sentiment_summary' in df_news.columns:
                        summary_sentiments = df_news['sentiment_summary'].head(news_count).apply(safe_capitalize).value_counts()
                    else:
                        summary_sentiments = {}
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Title Sentiments:**")
                        if title_sentiments.empty:
                            st.write("No title sentiment data available")
                        else:
                            for sentiment, count in title_sentiments.items():
                                icon, _ = get_sentiment_color(sentiment)
                                percentage = (count / news_count) * 100
                                st.write(f"{icon} {sentiment}: {count} ({percentage:.1f}%)")
                    
                    with col2:
                        st.write("**Summary Sentiments:**")
                        if summary_sentiments.empty:
                            st.write("No summary sentiment data available")
                        else:
                            for sentiment, count in summary_sentiments.items():
                                icon, _ = get_sentiment_color(sentiment)
                                percentage = (count / news_count) * 100
                                st.write(f"{icon} {sentiment}: {count} ({percentage:.1f}%)")
                                
                except Exception as e:
                    st.error(f"Error in sentiment analysis summary: {str(e)}")
                    st.write("Raw sentiment data types:")
                    if 'sentiment_title' in df_news.columns:
                        st.write(f"Title sentiments type: {type(df_news['sentiment_title'].iloc[0])}")
                    if 'sentiment_summary' in df_news.columns:
                        st.write(f"Summary sentiments type: {type(df_news['sentiment_summary'].iloc[0])}")
        
        else:
            st.warning(f"⚠️ No news articles found for {ticker}")
            st.info("💡 This could happen if:")
            st.write("- The ticker symbol is incorrect")
            st.write("- No recent news available for this stock")
            st.write("- RSS feed is temporarily unavailable")
            
    except ImportError:
        st.error("❌ stocknews package not installed!")
        st.code("pip install stocknews", language="bash")
        st.info("💡 Alternative: You can search for news manually on financial websites")
        
    except Exception as e:
        st.error(f"❌ Error loading news: {str(e)}")
        st.info("💡 Possible issues:")
        st.write("- Network connection problem")
        st.write("- RSS feed temporarily unavailable") 
        st.write("- Invalid ticker symbol")