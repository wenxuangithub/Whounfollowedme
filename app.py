import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from collections import Counter
from translations import translations

def get_text(key, lang='en'):
    return translations[lang].get(key, key)

def process_json_data(data, file_type):
    try:
        if file_type == "followers":
            df = pd.json_normalize(data)
        else:  # following
            df = pd.json_normalize(data['relationships_following'])
        
        df['username'] = df['string_list_data'].apply(lambda x: x[0]['value'])
        df['date'] = pd.to_datetime(df['string_list_data'].apply(lambda x: x[0]['timestamp']), unit='s')
        df['link'] = df['string_list_data'].apply(lambda x: x[0]['href'])
        df = df.drop(['title', 'media_list_data', 'string_list_data'], axis=1)
        return df
    except KeyError as e:
        raise ValueError(get_text('error_invalid_json', st.session_state.lang).format(file_type=file_type, error=str(e)))
    except Exception as e:
        raise ValueError(get_text('error_processing', st.session_state.lang).format(file_type=file_type, error=str(e)))

def load_data(uploaded_file, file_type):
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            return process_json_data(data, file_type)
        except json.JSONDecodeError:
            raise ValueError(get_text('error_invalid_file', st.session_state.lang).format(file_type=file_type))
    return None

def analyze_data(followers_df, following_df):
    if followers_df is not None and following_df is not None:
        followers = set(followers_df['username'])
        following = set(following_df['username'])
        not_following_back = following - followers
        not_followed_back = followers - following
        return not_following_back, not_followed_back
    return set(), set()

def find_most_active_time(df):
    df['hour'] = df['date'].dt.hour
    hour_counts = df['hour'].value_counts()
    most_active_hour = hour_counts.index[0]
    return f"{most_active_hour:02d}:00 - {(most_active_hour+1)%24:02d}:00"

def calculate_follower_loyalty(df):
    current_time = pd.Timestamp.now()
    df['loyalty_days'] = (current_time - df['date']).dt.days
    loyal_followers = df.nlargest(10, 'loyalty_days')
    return loyal_followers[['username', 'loyalty_days']]

def identify_seasonal_trends(df):
    df['month'] = df['date'].dt.month
    monthly_counts = df.groupby('month').size()
    peak_month = monthly_counts.idxmax()
    trough_month = monthly_counts.idxmin()
    return pd.to_datetime(peak_month, format='%m'), pd.to_datetime(trough_month, format='%m')

def create_growth_charts(followers_df, following_df):
    fig = make_subplots(rows=1, cols=2, subplot_titles=(get_text('follower_growth', st.session_state.lang), get_text('following_growth', st.session_state.lang)), horizontal_spacing=0.1)

    fig.add_trace(
        go.Histogram(x=followers_df['date'], nbinsx=50, name=get_text('followers', st.session_state.lang), marker_color='khaki'),
        row=1, col=1
    )

    fig.add_trace(
        go.Histogram(x=following_df['date'], nbinsx=50, name=get_text('following', st.session_state.lang), marker_color='dodgerblue'),
        row=1, col=2
    )

    fig.update_layout(
        height=500,
        title_text=get_text('growth_analysis', st.session_state.lang),
        showlegend=False
    )
    fig.update_xaxes(title_text=get_text('date', st.session_state.lang))
    fig.update_yaxes(title_text=get_text('count', st.session_state.lang))

    return fig

def display_growth_analysis(followers_df, following_df):
    st.header(get_text('follower_growth_detective', st.session_state.lang))

    fig = create_growth_charts(followers_df, following_df)
    st.plotly_chart(fig, use_container_width=True)

    loyal_followers = calculate_follower_loyalty(followers_df)
    st.subheader(get_text('loyal_followers', st.session_state.lang))
    st.dataframe(loyal_followers)

    most_active_time = find_most_active_time(followers_df)
    st.subheader(get_text('most_active_time', st.session_state.lang))
    st.write(get_text('most_active_time_desc', st.session_state.lang).format(time=most_active_time))

    peak_month, trough_month = identify_seasonal_trends(followers_df)
    st.subheader(get_text('seasonal_trends', st.session_state.lang))
    st.write(get_text('seasonal_trends_desc', st.session_state.lang).format(peak_month=peak_month.strftime('%B'), trough_month=trough_month.strftime('%B')))

def show_download_guide():
    st.markdown('')
    st.markdown(get_text('download_guide_title', st.session_state.lang))
    st.write(get_text('download_guide_intro', st.session_state.lang))

    steps = [
        get_text('step1', st.session_state.lang),
        get_text('step2', st.session_state.lang),
        get_text('step3', st.session_state.lang),
        get_text('step4', st.session_state.lang),
        get_text('step5', st.session_state.lang),
        get_text('step6', st.session_state.lang),
        get_text('step7', st.session_state.lang),
        get_text('step8', st.session_state.lang),
        get_text('step9', st.session_state.lang),
        get_text('step10', st.session_state.lang),
        get_text('step11', st.session_state.lang),
        get_text('step12', st.session_state.lang),
        get_text('step13', st.session_state.lang),
        get_text('step14', st.session_state.lang)
    ]

    for i, step in enumerate(steps, 1):
        st.write(f"{i}. {step}")

    st.info(get_text('download_guide_note', st.session_state.lang))

footer_html = """
<div style='text-align: center;'>
  <p>Developed with ❤️ by <a href='https://github.com/wenxuangithub' target='_blank'> Wen Xuan</a> </p>
</div>
"""

def main():
    st.set_page_config(layout="wide", page_title=get_text('page_title'), page_icon='😈')
    
    # Language selection
    lang = st.selectbox("Language / 语言", ['English', '中文'])
    st.session_state.lang = 'en' if lang == 'English' else 'zh'
    
    st.title(get_text('title', st.session_state.lang))
    st.sidebar.header(get_text('upload_header', st.session_state.lang))
    
    followers_file = st.sidebar.file_uploader(get_text('upload_followers', st.session_state.lang), type="json", key="followers")
    following_file = st.sidebar.file_uploader(get_text('upload_following', st.session_state.lang), type="json", key="following")
    
    try:
        followers_df = load_data(followers_file, "followers")
        following_df = load_data(following_file, "following")
        
        if followers_df is not None and following_df is not None:
            st.sidebar.success(get_text('data_loaded', st.session_state.lang))
            
            not_following_back, not_followed_back = analyze_data(followers_df, following_df)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(get_text('total_followers', st.session_state.lang), len(followers_df))
            col2.metric(get_text('total_following', st.session_state.lang), len(following_df))
            col3.metric(get_text('not_following_back', st.session_state.lang), len(not_following_back))
            col4.metric(get_text('you_dont_follow_back', st.session_state.lang), len(not_followed_back))
            
            ratio = len(followers_df) / len(following_df) if len(following_df) > 0 else 0
            st.metric(get_text('follower_ratio', st.session_state.lang), f"{ratio:.2f}")
            
            tab1, tab2, tab3 = st.tabs([get_text('growth_analysis', st.session_state.lang), 
                                        get_text('user_tables', st.session_state.lang), 
                                        get_text('user_search', st.session_state.lang)])
            
            with tab1:
                display_growth_analysis(followers_df, following_df)
            
            with tab2:
                st.header(get_text('relationship_board', st.session_state.lang))
                
                st.subheader(get_text('not_following_you_back', st.session_state.lang))
                not_following_back_df = pd.DataFrame(list(not_following_back), columns=['Username'])
                not_following_back_df['Following Since'] = not_following_back_df['Username'].map(following_df.set_index('username')['date'])
                not_following_back_df['Profile Link'] = not_following_back_df['Username'].map(following_df.set_index('username')['link'])
                st.dataframe(not_following_back_df.sort_values('Following Since', ascending=False), height=400, width=800)
                
                st.subheader(get_text('you_dont_follow_back_table', st.session_state.lang))
                not_followed_back_df = pd.DataFrame(list(not_followed_back), columns=['Username'])
                not_followed_back_df['Follower Since'] = not_followed_back_df['Username'].map(followers_df.set_index('username')['date'])
                not_followed_back_df['Profile Link'] = not_followed_back_df['Username'].map(followers_df.set_index('username')['link'])
                st.dataframe(not_followed_back_df.sort_values('Follower Since', ascending=False), height=400, width=800)
            
            with tab3:
                st.header(get_text('instagram_sherlock', st.session_state.lang))
                search_term = st.text_input(get_text('enter_username', st.session_state.lang))
                if search_term:
                    all_users = pd.concat([followers_df[['username']], following_df[['username']]])
                    all_users = all_users.drop_duplicates()
                    filtered_users = all_users[all_users['username'].str.contains(search_term, case=False)]
                    
                    if not filtered_users.empty:
                        st.write(get_text('search_results', st.session_state.lang))
                        for username in filtered_users['username']:
                            is_follower = username in followers_df['username'].values
                            is_following = username in following_df['username'].values
                            
                            if is_follower and is_following:
                                st.success(get_text('mutual_follow', st.session_state.lang).format(username=username))
                            elif is_follower:
                                st.info(get_text('follows_you', st.session_state.lang).format(username=username))
                            elif is_following:
                                st.warning(get_text('you_follow', st.session_state.lang).format(username=username))
                            else:
                                st.error(get_text('no_relationship', st.session_state.lang).format(username=username))
                    else:
                        st.write(get_text('no_matching_users', st.session_state.lang))
        else:
            st.subheader(get_text('subheader', st.session_state.lang))
            st.caption(get_text('caption', st.session_state.lang))
            st.warning(get_text('upload_warning', st.session_state.lang))
            show_download_guide()
        st.markdown(footer_html, unsafe_allow_html=True)

    except ValueError as e:
        st.error(f"{get_text('error', st.session_state.lang)}: {str(e)}")
        st.error(get_text('error_possible_issues', st.session_state.lang))
        st.error(get_text('error_invalid_json_file', st.session_state.lang))
        st.error(get_text('error_wrong_structure', st.session_state.lang))
        st.error(get_text('error_wrong_file', st.session_state.lang))
    except Exception as e:
        st.error(get_text('error_unexpected', st.session_state.lang))
        st.error(get_text('error_details', st.session_state.lang).format(error=str(e)))

if __name__ == "__main__":
    main()