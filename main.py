import pandas as pd
import numpy as np
import cv2
import streamlit as st
from PIL import Image
import io
import base64


st.set_page_config(page_title="Color Detection Tool", layout="centered")
st.title("🎨 Color Detection Tool")
st.markdown("Upload an image and click on it to detect the color at that point.")


@st.cache_data
def load_color_data():
    try:
        colors_df = pd.read_csv('colors.csv')
        colors_df.columns = colors_df.columns.str.strip() 
        return colors_df
    except FileNotFoundError:
        data = {
            'color_name_full': [
                'Black', 'White', 'Red', 'Lime', 'Blue', 'Yellow', 'Cyan', 'Magenta',
                'Silver', 'Gray', 'Maroon', 'Olive', 'Green', 'Purple', 'Teal', 'Navy'
            ],
            'hex_value': [
                '#000000', '#FFFFFF', '#FF0000', '#00FF00', '#0000FF', '#FFFF00', 
                '#00FFFF', '#FF00FF', '#C0C0C0', '#808080', '#800000', '#808000', 
                '#008000', '#800080', '#008080', '#000080'
            ],
            'R': [0, 255, 255, 0, 0, 255, 0, 255, 192, 128, 128, 128, 0, 128, 0, 0],
            'G': [0, 255, 0, 255, 0, 255, 255, 0, 192, 128, 0, 128, 128, 0, 128, 0],
            'B': [0, 255, 0, 0, 255, 0, 255, 255, 192, 128, 0, 0, 0, 128, 128, 128]
        }
        return pd.DataFrame(data)

colors_df = load_color_data()

def calculate_color_distance(rgb1, rgb2):
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

def get_closest_color(rgb):
    min_distance = float('inf')
    closest_color_name = ""
    closest_hex = "#000000"
    
    for _, row in colors_df.iterrows():
        r, g, b = int(row['R']), int(row['G']), int(row['B'])
        distance = calculate_color_distance(rgb, [r, g, b])
        if distance < min_distance:
            min_distance = distance
            closest_color_name = row['color_name_full']
            closest_hex = row['hex_value']
    
    return closest_color_name, closest_hex


uploaded_image = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'])

if uploaded_image:
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
 
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w, _ = image_rgb.shape

    st.image(image_rgb, caption="Uploaded Image", use_container_width=True)
   
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if 'image_rgb' not in st.session_state:
            st.session_state.image_rgb = image_rgb

        color_info = st.empty()
        
   
        clicked = st.button("Click on the image to detect color")
        
        if clicked:
            st.info("After clicking this button, your next click on the image will detect the color at that position.")

            st.markdown("""
            <style>
            canvas {
                cursor: crosshair !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
     
            cols = st.columns(2)
            with cols[0]:
                x = st.number_input("X coordinate", min_value=0, max_value=w-1, value=w//2)
            with cols[1]:
                y = st.number_input("Y coordinate", min_value=0, max_value=h-1, value=h//2)
    
            if 0 <= x < w and 0 <= y < h:
                rgb = image_rgb[y, x]
                r, g, b = rgb[0], rgb[1], rgb[2]
                
                color_name, hex_value = get_closest_color([r, g, b])
                
                with col2:
                    st.markdown(f"### 🎯 Detected Color at ({x}, {y})")
                    st.write(f"**RGB:** ({r}, {g}, {b})")
                    st.write(f"**Color Name:** {color_name}")
                    st.write(f"**Hex Code:** {hex_value}")
                    st.markdown(
                        f'<div style="width:100px;height:50px;background-color:{hex_value};border-radius:5px;"></div>',
                        unsafe_allow_html=True
                    )
            else:
                st.warning("Coordinates outside image bounds.")

    st.markdown("### 📊 Direct Coordinate Input")
    st.write("You can also input specific coordinates to check the color:")
    
    col1, col2 = st.columns(2)
    with col1:
        direct_x = st.number_input("Enter X coordinate", min_value=0, max_value=w-1, value=w//2, key="direct_x")
    with col2:
        direct_y = st.number_input("Enter Y coordinate", min_value=0, max_value=h-1, value=h//2, key="direct_y")
    
    check_color = st.button("Check Color at Coordinates")
    
    if check_color:
        if 0 <= direct_x < w and 0 <= direct_y < h:
            rgb = image_rgb[direct_y, direct_x]
            r, g, b = rgb[0], rgb[1], rgb[2]
            
            color_name, hex_value = get_closest_color([r, g, b])
            
            st.markdown("### 🔍 Color Information")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write(f"**RGB:** ({r}, {g}, {b})")
                st.write(f"**Color Name:** {color_name}")
                st.write(f"**Hex Code:** {hex_value}")
            
            with col2:
                st.markdown(
                    f'<div style="width:100px;height:100px;background-color:{hex_value};border-radius:5px;"></div>',
                    unsafe_allow_html=True
                )
        else:
            st.warning("Coordinates outside image bounds.")
else:
    st.info("Please upload an image to begin color detection.")
