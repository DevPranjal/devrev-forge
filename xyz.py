import streamlit as st
from sources import get_news, get_playstore_reviews, get_appstore_reviews, get_hackernews_posts, get_reddit_posts, get_twitter_posts
from textblob import TextBlob

reddit_query = {
    'Adobe Acrobat': 'adobe acrobat',
    'Adobe Photoshop': 'adobe photoshop',
    'Adobe Illustrator/Capture': 'adobe illustrator',
    'Adobe Premiere Pro/Rush': 'adobe premiere'
}

twitter_query = {
    'Adobe Acrobat': 'adobe acrobat',
    'Adobe Photoshop': 'adobe photoshop',
    'Adobe Illustrator/Capture': 'adobe illustrator',
    'Adobe Premiere Pro/Rush': 'adobe premiere'
}

appstore_appid = {
    'Adobe Acrobat': 469337564,
    'Adobe Photoshop': 457771281,
    'Adobe Illustrator/Capture': 1018784575,
    'Adobe Premiere Pro/Rush': 1188753863
}

appstore_appname = {
    'Adobe Acrobat': 'adobe-acrobat-reader-edit-pdf',
    'Adobe Photoshop': 'adobe-photoshop',
    'Adobe Illustrator/Capture': 'adobe-illustrator-graphic-art',
    'Adobe Premiere Pro/Rush': 'adobe-premiere-rush-edit-video'
}

playstore_appid = {
    'Adobe Acrobat': 'com.adobe.reader',
    'Adobe Photoshop': 'com.adobe.psmobile',
    'Adobe Illustrator/Capture': 'com.adobe.creativeapps.gather',
    'Adobe Premiere Pro/Rush': 'com.adobe.premiererush.videoeditor'
}

############### utils ###############

st.title('Adobe\'s Voice of Customer')

st.sidebar.subheader('Product')
product = st.sidebar.selectbox('Product', ['Adobe Acrobat', 'Adobe Photoshop', 'Adobe Illustrator/Capture', 'Adobe Premiere Pro/Rush'])
additional_query = st.sidebar.text_input('Additional Query')

st.sidebar.subheader('Channels')
reddit = st.sidebar.checkbox('Reddit')
twitter = st.sidebar.checkbox('Twitter')
appstore = st.sidebar.checkbox('AppStore')
playstore = st.sidebar.checkbox('Playstore')
hackernews = st.sidebar.checkbox('HackerNews')
mails = st.sidebar.checkbox('Mails')


st.sidebar.subheader('Since when?')
since = st.sidebar.date_input('Since', key='since')

st.sidebar.markdown('---')
fetch_data = st.sidebar.button('Fetch Data', type='primary')

tab1, tab2, tab3, tab4 = st.tabs(['Customer Issues', 'Sentiment', 'Clustered Topics', 'Product Reach'])

with tab1:
    col1, col2, _, _ = st.columns(4)
    with col1:
        summarize_tickets = st.button('Summarize', type='primary')
        
    with col2:
        merge_tickets = st.button('Merge Duplicates', type='primary')

with st.spinner('Fetching data...'):
    if fetch_data:
        reddit_posts = get_reddit_posts(f'{reddit_query[product]} {additional_query}', 'Adobe', 5000) if reddit else {}
        reddit_posts = [post for post in reddit_posts if post['created'] > since] if reddit else {}
        appstore_reviews = get_appstore_reviews(appstore_appname[product], appstore_appid[product], 1000) if appstore else {}
        appstore_reviews = [review for review in appstore_reviews if review['at'] > since] if appstore else {}
        playstore_reviews = get_playstore_reviews(playstore_appid[product], 1000) if playstore else {}
        playstore_reviews = [review for review in playstore_reviews if review['at'] > since] if playstore else {}
        hackernews_posts = get_hackernews_posts(f'{product if product != "All" else "adobe"} {additional_query}', 1000) if hackernews else {}
        hackernews_posts = [post for post in hackernews_posts if post['created'] > since] if hackernews else {}
        twitter_posts = get_twitter_posts(f'{reddit_query[product]} {additional_query}', since) if twitter else {}


if fetch_data:
    with tab1:
        with st.spinner('Creating tickets'):
            # create dataframe of all the data
            import pandas as pd
            df = pd.DataFrame(columns = ['Content', 'Channel', 'Created At'])
            if reddit:
                df = pd.concat([df, pd.DataFrame([[post['title'] + ' : ' + post['body'], 'Reddit', post['created']] for post in reddit_posts], columns = ['Content', 'Channel', 'Created At'])], ignore_index=True)
            if appstore:
                df = pd.concat([df, pd.DataFrame([[review['content'], 'AppStore', review['at']] for review in appstore_reviews], columns = ['Content', 'Channel', 'Created At'])], ignore_index=True)
            if playstore:
                df = pd.concat([df, pd.DataFrame([[review['content'], 'PlayStore', review['at']] for review in playstore_reviews], columns = ['Content', 'Channel', 'Created At'])], ignore_index=True)
            if hackernews:
                df = pd.concat([df, pd.DataFrame([[post['title'] + ' : ' + post['content'], 'HackerNews', post['created']] for post in hackernews_posts], columns = ['Content', 'Channel', 'Created At'])], ignore_index=True)
            if twitter:
                df = pd.concat([df, pd.DataFrame([[post['text'], 'Twitter', post['creation_date']] for post in twitter_posts], columns = ['Content', 'Channel', 'Created At'])], ignore_index=True)

            if "original_df" not in st.session_state:
                st.session_state["original_df"] = df.copy()

            st.dataframe(df)


if summarize_tickets:
    with st.spinner('Summarizing tickets...'):
        import google.generativeai as genai
        
        GOOGLE_API_KEY="AIzaSyDEbITaVUHwJoryven2aXOECow0IsW-e8I"
        genai.configure(api_key=GOOGLE_API_KEY)
        llm = genai.GenerativeModel('gemini-pro')

        df = st.session_state["original_df"].copy()
        print(df)

        for i, row in df.iterrows():
            comment = row['Content']
            prompt= "Generate a concise, crisp title (but do consider important details) for the following comment:  " + comment + "\n Just focus on the content, dont give the solution to the query, just the title."
            response = llm.generate_content(comment)
            df.at[i, 'Summary'] = response.text

        df.drop('Content', axis=1, inplace=True)
        st.dataframe(df)


if fetch_data:
    with tab2:
        with st.spinner('Analysing data...'):
            negative_reddit_posts = [post for post in reddit_posts if TextBlob(post['title'] + ' : ' + post['body']).sentiment.polarity < 1] if reddit else {}
            negative_appstore_reviews = [review for review in appstore_reviews if TextBlob(review['content']).sentiment.polarity < 1] if appstore else {}
            negative_playstore_reviews = [review for review in playstore_reviews if TextBlob(review['content']).sentiment.polarity < 1] if playstore else {}
            negative_hackernews_posts = [post for post in hackernews_posts if TextBlob(post['title'] + ' : ' + post['content']).sentiment.polarity < 1] if hackernews else {}
            negative_twitter_posts = [post for post in twitter_posts if TextBlob(post['text']).sentiment.polarity < 1] if twitter else {}

            # number of negative sentiments over time for each channel
            # group by date, count the number of negative sentiments
            reddit_sentiments = {}
            appstore_sentiments = {}
            playstore_sentiments = {}
            hackernews_sentiments = {}
            twitter_sentiments = {}

            for post in negative_reddit_posts:
                date = post['created']
                if date in reddit_sentiments:
                    reddit_sentiments[date] += 1
                else:
                    reddit_sentiments[date] = 1

            for review in negative_appstore_reviews:
                date = review['at']
                if date in appstore_sentiments:
                    appstore_sentiments[date] += 1
                else:
                    appstore_sentiments[date] = 1

            for review in negative_playstore_reviews:
                date = review['at']
                if date in playstore_sentiments:
                    playstore_sentiments[date] += 1
                else:
                    playstore_sentiments[date] = 1

            for post in negative_hackernews_posts:
                date = post['created']
                if date in hackernews_sentiments:
                    hackernews_sentiments[date] += 1
                else:
                    hackernews_sentiments[date] = 1

            for post in negative_twitter_posts:
                date = post['creation_date']
                if date in twitter_sentiments:
                    twitter_sentiments[date] += 1
                else:
                    twitter_sentiments[date] = 1

            # create dataframe
            import pandas as pd
            df = pd.DataFrame({
                'Reddit': reddit_sentiments,
                'AppStore': appstore_sentiments,
                'PlayStore': playstore_sentiments,
                'HackerNews': hackernews_sentiments,
                'Twitter': twitter_sentiments
            })

            st.line_chart(df)