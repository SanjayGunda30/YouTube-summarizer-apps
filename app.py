import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables from .env file
load_dotenv()

# Configure the Google API
api_key = os.getenv("Google_API_KEY")
if not api_key:
    st.error("Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
else:
    genai.configure(api_key=api_key)

# Function to extract video id from youtube url
def extract_video_id(url):
    pattern = [
        r"youtube.com/watch\?v=([^&]+)",
        r"youtu\.be/([^?]+)",
        r"youtube.com/embed/([^?]+)"
    ]
    for p in pattern:
        match = re.search(p, url)
        if match:
            return match.group(1)
    return None

# Function to get the video transcript
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        text = " ".join([entry["text"] for entry in transcript])
        return text[:3000] # Return only the first 3000 characters
    except Exception as e:
        st.write(f"Error getting transcript in English: {e}")
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            text = " ".join([entry["text"] for entry in transcript])
            return text[:3000] # Return only the first 3000 characters
        except Exception as e:
            st.write(f"Error getting transcript in other languages: {e}")
            return None

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

# Function to generate summary
def get_summary(text):
    response = model.generate_content(text)
    return response.text

# Initialize our Streamlit app
st.set_page_config(page_title="VideoTranscript AI")
st.header("VideoTranscript AI application")
url = st.text_input("Enter the YouTube video URL(only English Video)", key="input")

submit = st.button("Submit")  # Button to submit the question
# When the submit button is clicked
if submit:
    with st.spinner("Extracting video ID..."):
        video_id = extract_video_id(url)
        if video_id:
            with st.spinner("Extracting video transcript..."):
                transcript = get_transcript(video_id)
                if transcript:
                    with st.spinner("Generating summary..."):
                        response = get_summary(transcript)
                        st.subheader("Summary:")
                        st.write(response)  # Display the response
                else:
                    st.write("Error getting transcript")
        else:
            st.write("Invalid URL")

