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
import speech_recognition as sr
import requests
from io import BytesIO
from fpdf import FPDF
import pocketsphinx  # Alternative to speech_recognition

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

# PDF to Image Conversion
def pdf_to_image(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            image_list = []
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                image = page.to_image()
                image_buffer = io.BytesIO()
                image.save(image_buffer, format="PNG")
                image_buffer.seek(0)
                image_list.append(image_buffer)
            return image_list
    except Exception as e:
        st.error(f"Error converting PDF to image: {e}")

# Speech-to-Text (Audio File to Text)
def audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    audio_data = sr.AudioFile(audio_file)
    with audio_data as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except Exception as e:
        st.error(f"Error recognizing speech: {e}")
        return None

# Currency Converter
def convert_currency(amount, from_currency, to_currency):
    api_url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    response = requests.get(api_url)
    data = response.json()
    rate = data['rates'].get(to_currency)
    if rate:
        return amount * rate
    else:
        st.error(f"Error fetching exchange rates for {to_currency}")
        return None

# Image Slideshow
def create_image_slideshow(images):
    if len(images) > 0:
        for img in images:
            st.image(img, use_column_width=True)

# Markdown to PDF Conversion
def markdown_to_pdf(md_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, md_content)
    pdf_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(pdf_output.name)  # Write to a file
    return pdf_output.name  # Return the file path

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

# Currency Converter
amount = st.number_input("Enter Amount for Currency Conversion", min_value=0.0)
from_currency = st.selectbox("Select From Currency", ["USD", "EUR", "GBP", "INR", "JPY"])
to_currency = st.selectbox("Select To Currency", ["USD", "EUR", "GBP", "INR", "JPY"])

if st.button("Convert Currency"):
    try:
        converted_amount = convert_currency(amount, from_currency, to_currency)
        if converted_amount:
            st.write(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")
    except Exception as e:
        st.error(f"Error converting currency: {e}")

# Image Slideshow
image_files = st.file_uploader("Upload Images for Slideshow", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if image_files:
    create_image_slideshow([Image.open(img) for img in image_files])

# Audio File to Text (Speech Recognition)
audio_file = st.file_uploader("Upload Audio File for Speech Recognition", type=["wav", "mp3", "flac"])
if audio_file:
    if st.button("Convert Audio to Text"):
        try:
            recognizer = sr.Recognizer()
            audio_data = sr.AudioFile(audio_file)
            with audio_data as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            st.write("Converted Text:")
            st.write(text)
        except Exception as e:
            st.error(f"Error converting audio to text: {e}")

# Markdown to PDF Conversion
md_content_for_pdf = st.text_area("Enter Markdown Content for PDF Conversion")
if st.button("Convert Markdown to PDF"):
    try:
        pdf_output_path = markdown_to_pdf(md_content_for_pdf)
        with open(pdf_output_path, "rb") as pdf_file:
            st.download_button("Download PDF", pdf_file, file_name="converted_document.pdf")
    except Exception as e:
        st.error(f"Error converting Markdown to PDF: {e}")
