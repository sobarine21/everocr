import streamlit as st
import pdfplumber
from markdown import markdown
from docx import Document
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import resize as video_resize
import pandas as pd
from PIL import Image, ImageFilter
import io
import qrcode
import random
import string
from gtts import gTTS
import os
import tempfile
import zipfile
import base64
import hashlib
from cryptography.fernet import Fernet
import io

# Utility Functions

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def create_qr_code(data):
    qr = qrcode.make(data)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def visualize_data(df):
    st.line_chart(df)

# File Encryption/Decryption Functions
def encrypt_file(file_data, password):
    key = hashlib.sha256(password.encode()).digest()
    cipher_suite = Fernet(base64.urlsafe_b64encode(key[:32]))
    encrypted_data = cipher_suite.encrypt(file_data)
    return encrypted_data

def decrypt_file(file_data, password):
    key = hashlib.sha256(password.encode()).digest()
    cipher_suite = Fernet(base64.urlsafe_b64encode(key[:32]))
    decrypted_data = cipher_suite.decrypt(file_data)
    return decrypted_data

# Streamlit App Layout
st.title("Enhanced File Type Converters & Media Processing")

# File Type Conversion Section
st.header("File Type Converters")

# PDF to Word Converter
pdf_file = st.file_uploader("Upload PDF Document for PDF to Word Conversion", type="pdf")
if pdf_file:
    try:
        if st.button("Convert PDF to Word"):
            with pdfplumber.open(pdf_file) as pdf:
                doc = Document()
                for page in pdf.pages:
                    doc.add_paragraph(page.extract_text())
                word_file = io.BytesIO()
                doc.save(word_file)
                word_file.seek(0)
                st.download_button("Download Word Document", word_file, file_name="converted_document.docx")
    except Exception as e:
        st.error(f"Error converting PDF to Word: {e}")

# Markdown to HTML Converter
markdown_content = st.text_area("Enter Markdown Content for Conversion to HTML")
if st.button("Convert Markdown to HTML"):
    try:
        html_output = markdown(markdown_content)
        st.write("### HTML Output")
        st.code(html_output, language="html")
    except Exception as e:
        st.error(f"Error converting Markdown to HTML: {e}")

# Image Format Conversion (Improved Bytes-like object handling)
uploaded_image = st.file_uploader("Upload Image (JPG/PNG) for Format Conversion", type=["jpg", "jpeg", "png"])
if uploaded_image:
    try:
        img = Image.open(uploaded_image)
        format_choice = st.selectbox("Convert to Format", options=["PNG", "JPEG"])
        output_buffer = io.BytesIO()
        
        # Using the LANCZOS resampling method instead of ANTIALIAS
        if st.button("Convert Image Format"):
            img = img.resize((img.width // 2, img.height // 2), Image.Resampling.LANCZOS)  # Resize image
            img.save(output_buffer, format=format_choice)
            output_buffer.seek(0)
            st.image(output_buffer, caption=f"Converted Image in {format_choice} format", use_column_width=True)
    except Exception as e:
        st.error(f"Error converting image format: {e}")

# Media Processing Section
st.header("Media Processing Features")

# Video Resizer
uploaded_video = st.file_uploader("Upload Video File for Resizing", type=["mp4", "avi"])
if uploaded_video:
    try:
        # Save the uploaded video file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(uploaded_video.read())
            temp_video_path = temp_video.name
        
        # Load the video using MoviePy
        video_clip = VideoFileClip(temp_video_path)
        scale_factor = st.slider("Select Resize Scale Factor", min_value=0.1, max_value=1.0, value=0.5)
        
        if st.button("Resize Video"):
            resized_clip = video_clip.fx(video_resize, scale_factor)
            resized_video_buffer = io.BytesIO()
            resized_clip.write_videofile(resized_video_buffer)
            resized_video_buffer.seek(0)
            st.video(resized_video_buffer, format="video/mp4")
    except Exception as e:
        st.error(f"Error resizing video: {e}")

# QR Code Generator
qr_data = st.text_input("Enter data for QR Code")
if st.button("Generate QR Code"):
    try:
        qr_image = create_qr_code(qr_data)
        st.image(qr_image, caption="QR Code")
        st.download_button("Download QR Code", qr_image, file_name="qrcode.png")
    except Exception as e:
        st.error(f"Error generating QR code: {e}")

# Random Password Generator
if st.button("Generate Random Password"):
    try:
        password = generate_random_password()
        st.write(f"Generated Password: {password}")
    except Exception as e:
        st.error(f"Error generating password: {e}")

# Data Visualization
data_file = st.file_uploader("Upload CSV for Visualization", type="csv")
if data_file:
    try:
        df = pd.read_csv(data_file)
        visualize_data(df)
    except Exception as e:
        st.error(f"Error processing CSV file: {e}")

# Speech Conversion (Text-to-Speech)
text_to_speech_input = st.text_area("Enter Text for Text-to-Speech Conversion")
if st.button("Convert Text to Speech"):
    try:
        tts = gTTS(text=text_to_speech_input, lang='en')
        audio_buffer = io.BytesIO()
        tts.save(audio_buffer)
        audio_buffer.seek(0)
        st.audio(audio_buffer, format="audio/mp3")
    except Exception as e:
        st.error(f"Error converting text to speech: {e}")

# New Features

# Text File Upload and Display
text_file = st.file_uploader("Upload Text File", type="txt")
if text_file:
    try:
        content = text_file.read().decode("utf-8")
        st.text_area("File Content", content, height=200)
    except Exception as e:
        st.error(f"Error displaying text file: {e}")

# Image Effects
if uploaded_image:
    effect = st.selectbox("Apply Image Effect", ["None", "Grayscale", "Blur", "Sharpen"])
    if st.button("Apply Effect"):
        try:
            if effect == "Grayscale":
                img = img.convert("L")
            elif effect == "Blur":
                img = img.filter(ImageFilter.BLUR)
            elif effect == "Sharpen":
                img = img.filter(ImageFilter.SHARPEN)
            st.image(img, caption=f"Image with {effect} effect", use_column_width=True)
        except Exception as e:
            st.error(f"Error applying image effect: {e}")

# File Compression
uploaded_file = st.file_uploader("Upload File for Compression (Text or Image)", type=["txt", "jpg", "jpeg", "png"])
if uploaded_file:
    if st.button("Compress File"):
        try:
            compressed_file_buffer = io.BytesIO()
            with zipfile.ZipFile(compressed_file_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr(uploaded_file.name, uploaded_file.getvalue())
            compressed_file_buffer.seek(0)
            st.download_button("Download Compressed File", compressed_file_buffer, file_name="compressed_file.zip")
        except Exception as e:
            st.error(f"Error compressing file: {e}")

# Video to Audio Conversion
uploaded_video = st.file_uploader("Upload Video for Audio Extraction", type=["mp4", "avi"])
if uploaded_video:
    if st.button("Extract Audio"):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                temp_video.write(uploaded_video.read())
                temp_video_path = temp_video.name
            
            video_clip = VideoFileClip(temp_video_path)
            audio_clip = video_clip.audio
            audio_buffer = io.BytesIO()
            audio_clip.write_audiofile(audio_buffer)
            audio_buffer.seek(0)
            st.audio(audio_buffer, format="audio/mp3")
        except Exception as e:
            st.error(f"Error extracting audio: {e}")

# Palindrome Checker
text = st.text_input("Enter text to check if it's a Palindrome")
if st.button("Check Palindrome"):
    try:
        if text == text[::-1]:
            st.success("This is a palindrome!")
        else:
            st.error("This is not a palindrome.")
    except Exception as e:
        st.error(f"Error checking palindrome: {e}")

# File Encryption/Decryption
uploaded_file = st.file_uploader("Upload File for Encryption/Decryption", type=["txt", "jpg", "png"])
if uploaded_file:
    password = st.text_input("Enter Password for Encryption/Decryption", type="password")
    if st.button("Encrypt File"):
        try:
            encrypted_data = encrypt_file(uploaded_file.read(), password)
            st.download_button("Download Encrypted File", encrypted_data, file_name="encrypted_file")
        except Exception as e:
            st.error(f"Error encrypting file: {e}")
    if st.button("Decrypt File"):
        try:
            decrypted_data = decrypt_file(uploaded_file.read(), password)
            st.download_button("Download Decrypted File", decrypted_data, file_name="decrypted_file")
        except Exception as e:
            st.error(f"Error decrypting file: {e}")

# Clean up temporary files
temp_files = ["converted_html.pdf", "resized_video.mp4"]
for temp_file in temp_files:
    if os.path.exists(temp_file):
        os.remove(temp_file)
