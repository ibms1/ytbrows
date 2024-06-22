import streamlit as st
import pandas as pd
import time
import datetime
from googleapiclient.discovery import build

# إعداد واجهة المستخدم باستخدام Streamlit
st.title("Finding Viral YouTube Videos in Last 24 Hours")
st.write("This tool continuously searches for viral YouTube videos published in the last 24 hours.")

# إعداد API الخاص بيوتيوب
api_key = "AIzaSyCMsj5PfQu_SBNvVj_ge1qVUKbwKA0n2xs"
youtube = build('youtube', 'v3', developerKey=api_key)

# إضافة تنسيق CSS لإخفاء الروابط عند تمرير الفأرة فوق النصوص
hide_links_style = """
    <style>
    a {
        text-decoration: none;
        color: inherit;
        pointer-events: none;
    }
    a:hover {
        text-decoration: none;
        color: inherit;
        cursor: default;
    }
    </style>
    """
st.markdown(hide_links_style, unsafe_allow_html=True)

# دالة لجلب الفيديوهات
def get_viral_videos():
    one_day_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat("T") + "Z"
    search_response = youtube.search().list(
        part='snippet',
        publishedAfter=one_day_ago,
        order='viewCount',
        type='video',
        maxResults=50
    ).execute()

    video_data = []

    for search_result in search_response.get('items', []):
        video_id = search_result['id']['videoId']
        video_title = search_result['snippet']['title']
        video_thumbnail = search_result['snippet']['thumbnails']['default']['url']
        
        video_response = youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()

        if video_response['items']:
            video_views = int(video_response['items'][0]['statistics']['viewCount'])

        channel_id = search_result['snippet']['channelId']
        channel_response = youtube.channels().list(
            part='statistics',
            id=channel_id
        ).execute()

        if channel_response['items']:
            channel_subscribers = int(channel_response['items'][0]['statistics']['subscriberCount'])
            
            if channel_subscribers < 500000:  # فلترة الفيديوهات للقنوات التي تحتوي على أقل من 500,000 مشترك
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                video_data.append([video_title, video_thumbnail, video_views, channel_subscribers, video_url])

    return video_data

# عرض الرسالة المستمرة "Loading Videos..."
loading_message = st.empty()
loading_message.text("Loading Videos...")

# جدول لعرض النتائج
placeholder = st.empty()

while True:
    video_data = get_viral_videos()

    if video_data:
        df = pd.DataFrame(video_data, columns=["Video Title", "Thumbnail", "Views", "Subscribers", "URL"])

        # عرض النتائج في جدول
        with placeholder.container():
            for index, row in df.iterrows():
                st.write(f"**{row['Video Title']}**")
                st.markdown(f'<a href="{row["URL"]}" target="_blank"><img src="{row["Thumbnail"]}" width="100"></a>', unsafe_allow_html=True)
                st.write(f"Views: {row['Views']}")
                st.write(f"Subscribers: {row['Subscribers']}")
                st.write("---")

    time.sleep(3600)  # البحث كل ساعة
