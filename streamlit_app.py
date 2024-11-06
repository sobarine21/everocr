import streamlit as st
from moviepy.editor import VideoFileClip
from docx import Document
import pandas as pd
import os
from PIL import Image
import tempfile
import qrcode
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import random
import string

# Utility Functions
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def create_qr_code(data):
    qr = qrcode.make(data)
    return qr

def visualize_data(df):
    st.line_chart(df)

# Set up the Streamlit app title
st.title("Advanced File Type Converters & Media Processing")

# File Type Conversion Section
st.header("File Type Converters")

# PDF to Word Converter
if st.file_uploader("Upload PDF Document", type=["pdf"]):
    if st.button("Convert to Word"):
        # Placeholder for actual PDF to Word conversion
        st.write("PDF to Word conversion is not implemented in this version.")

# Image Resizer
uploaded_image = st.file_uploader("Upload Image (JPG/PNG)", type=["jpg", "jpeg", "png"])
if uploaded_image:
    img = Image.open(uploaded_image)
    width = st.number_input("Set Width", value=img.size[0])
    height = st.number_input("Set Height", value=img.size[1])
    if st.button("Resize Image"):
        resized_image = img.resize((width, height))
        st.image(resized_image, caption="Resized Image")
        resized_image.save("resized_image.png")
        st.download_button("Download Resized Image", "resized_image.png")

# Image Compressor
if st.button("Compress Image"):
    img.save("compressed_image.png", optimize=True, quality=85)
    st.download_button("Download Compressed Image", "compressed_image.png")

# CSV to Excel Converter
csv_file = st.file_uploader("Upload CSV File", type=["csv"])
if csv_file:
    df = pd.read_csv(csv_file)
    if st.button("Convert CSV to Excel"):
        excel_file = "converted_file.xlsx"
        df.to_excel(excel_file, index=False)
        st.download_button("Download Excel File", excel_file)

# Excel to CSV Converter
excel_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if excel_file:
    df = pd.read_excel(excel_file)
    if st.button("Convert Excel to CSV"):
        csv_file = "converted_file.csv"
        df.to_csv(csv_file, index=False)
        st.download_button("Download CSV File", csv_file)

# HTML to PDF Converter
html_content = st.text_area("Enter HTML Content")
if st.button("Convert HTML to PDF"):
    st.write("HTML to PDF conversion is not implemented in this version.")

# Markdown to HTML Converter
markdown_content = st.text_area("Enter Markdown Content")
if st.button("Convert Markdown to HTML"):
    st.write("Markdown to HTML conversion is not implemented in this version.")

# Media Processing Section
st.header("Media Processing Features")

# Video to Audio Converter
uploaded_video = st.file_uploader("Upload Video File", type=["mp4", "avi"])
if uploaded_video:
    if st.button("Extract Audio"):
        video_clip = VideoFileClip(uploaded_video)
        audio_file = "extracted_audio.mp3"
        video_clip.audio.write_audiofile(audio_file)
        st.download_button("Download Extracted Audio", audio_file)

# Audio Trimmer
audio_file = st.file_uploader("Upload Audio File", type=["mp3", "wav"])
if audio_file:
    start_time = st.number_input("Start Time (seconds)", 0)
    end_time = st.number_input("End Time (seconds)", 30)
    if st.button("Trim Audio"):
        audio_clip = VideoFileClip(audio_file)
        trimmed_audio = audio_clip.subclip(start_time, end_time)
        trimmed_audio.write_audiofile("trimmed_audio.mp3")
        st.download_button("Download Trimmed Audio", "trimmed_audio.mp3")

# Video Resizer
if st.button("Resize Video"):
    # Placeholder for video resizing functionality
    st.write("Video resizing is not implemented in this version.")

# Audio Merger
audio_files = st.file_uploader("Upload Multiple Audio Files", type=["mp3", "wav"], accept_multiple_files=True)
if audio_files:
    if st.button("Merge Audio Files"):
        combined = AudioSegment.empty()
        for file in audio_files:
            audio = AudioSegment.from_file(file)
            combined += audio
        combined.export("merged_audio.mp3", format="mp3")
        st.download_button("Download Merged Audio", "merged_audio.mp3")

# QR Code Generator
qr_data = st.text_input("Enter data for QR Code")
if st.button("Generate QR Code"):
    qr_image = create_qr_code(qr_data)
    st.image(qr_image)

# Markdown Preview
if st.button("Preview Markdown"):
    st.markdown(markdown_content)

# Random Password Generator
if st.button("Generate Random Password"):
    password = generate_random_password()
    st.write(f"Generated Password: {password}")

# Data Visualization
data_file = st.file_uploader("Upload CSV for Visualization", type=["csv"])
if data_file:
    df = pd.read_csv(data_file)
    visualize_data(df)

# File Metadata Viewer
uploaded_file = st.file_uploader("Upload Any File", type=["*"])
if uploaded_file:
    if st.button("View File Metadata"):
        file_info = {
            "File Name": uploaded_file.name,
            "File Size (bytes)": uploaded_file.size,
            "File Type": uploaded_file.type
        }
        st.json(file_info)

# Clean up temporary files
if os.path.exists("resized_image.png"):
    os.remove("resized_image.png")
if os.path.exists("extracted_audio.mp3"):
    os.remove("extracted_audio.mp3")
if os.path.exists("trimmed_audio.mp3"):
    os.remove("trimmed_audio.mp3")
if os.path.exists("merged_audio.mp3"):
    os.remove("merged_audio.mp3")
