import streamlit as st
import pandas as pd
import numpy as np
import re
from PIL import Image
import plotly.express as px

# 1. Define U-values for all materials
# 1. Define U-values for all materials
U_VALUES = {
    "Single Glazed Glass": 5.7,
    "Double Glazed Glass": 2.8,
    "Steel": 5.7,
    "Concrete": 3.0,
    "Vent Polymer (ABS/PVC)": 3.0,
    "PVC Single Glazed": 4.8, 
    "PVC Double Glazed": 2.8, 
    "PVC Triple Glazed": 2.1,
    "Solid Wood Door": 3.0, 
    "Glazed Wood Single": 5.7, 
    "Glazed Wood Double": 3.4,
    "Glazed Wood Triple": 2.6, 
    "Metal Single": 5.7, 
    "Metal Double": 3.4, 
    "Metal Triple": 2.6,
    "Solid Brick": 2.1, 
    "Solid Brick Insulated": 0.28, 
    "Solid Stone": 2.25,
    "Solid Stone Insulated": 0.32, 
    "Solid Concrete": 3.0, 
    "Solid Concrete Insulated": 0.31,
    "Cavity Wall Uninsulated": 1.3, 
    "Cavity Wall Insulated": 0.55, 
    "Hardwood": 0.18,
    "Softwood": 0.13, 
    "Plasterboard": 0.16
}

# 2. Initialize session state
if 'materials' not in st.session_state:
    st.session_state.materials = {}
# 新增：用于在切换标签时永久保存 Overview 里的两张主图
if 'main_images_cache' not in st.session_state:
    st.session_state.main_images_cache = []

# Set page layout
st.set_page_config(layout="wide", page_title="Thermal Image Analyzer")

# --- SIDEBAR & GLOBAL SETTINGS ---
st.sidebar.title("Settings & Navigation")

# Environmental temperature input (Global)
env_temp = st.sidebar.number_input("Environmental Temperature (°C)", value=20.0, step=0.1)

# File uploader for up to 20 thermal images
uploaded_files = st.sidebar.file_uploader(
    "Upload Thermal Images (Max 20)", 
    accept_multiple_files=True, 
    type=['png', 'jpg', 'jpeg']
)

# Enforce max 20 files rule
if len(uploaded_files) > 20:
    st.sidebar.warning("Maximum 20 files allowed. Only processing the first 20.")
    uploaded_files = uploaded_files[:20]

# 3. Parse filenames to extract photo name and temperatures
parsed_data = {}
pattern = r"^(.*?)\(([-+]?\d*\.?\d+)\s+([-+]?\d*\.?\d+)\s+([-+]?\d*\.?\d+)\)(?:\.[a-zA-Z0-9]+)?$"

for file in uploaded_files:
    match = re.match(pattern, file.name)
    if match:
        name, avg_t, max_t, min_t = match.groups()
        parsed_data[name] = {
            "file": file,
            "avg": float(avg_t),
            "max": float(max_t),
            "min": float(min_t),
            "original_name": file.name
        }
    else:
        st.sidebar.error(f"Invalid format: {file.name}. Expected: Name(avg max min)")

# 4. Navigation
tabs = ["Overview"] + list(parsed_data.keys())
selected_tab = st.sidebar.radio("Navigation Menu", tabs)

# --- Overview ---
if selected_tab == "Overview":
    st.title("Overview")
    
    st.subheader("Main Entrance & Thermal Images")
    
    # 合并的上传组件
    main_images = st.file_uploader(
        "Upload Main Entrance and Thermal Image (Select up to 2 files)", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True, 
        key="main_imgs"
    )
    
    # 只要用户上传了新照片，立刻把它们解析并存入 Session State 缓存
    if main_images:
        if len(main_images) > 2:
            st.warning("You uploaded more than 2 files. Only keeping the first two.")
            
        new_cache = []
        for file in main_images[:2]:
            img = Image.open(file)
            new_cache.append(img)
        st.session_state.main_images_cache = new_cache

    # 如果缓存里有照片，就显示它们，并提供一个清除按钮
    if st.session_state.main_images_cache:
        if st.button("Clear Main Images"):
            st.session_state.main_images_cache = []
            st.rerun() # 刷新页面
            
        # 布局调整：两边各留 15% 空白，中间两个图片各占 35% (相比原本的 50% 刚好缩小 30%)
        spacer_left, col1, col2, spacer_right = st.columns([0.15, 0.35, 0.35, 0.15])
        
        cache = st.session_state.main_images_cache
        if len(cache) >= 1:
            with col1:
                st.caption("Main Thermal Image")
                st.image(cache[0], use_container_width=True)
        if len(cache) >= 2:
            with col2:
                st.caption("Main Entrance Photo")
                st.image(cache[1], use_container_width=True)

    # Calculate summary table if there are parsed thermal images
    if parsed_data:
        st.markdown("---")
        st.subheader("Thermal Analysis Summary")
        
        summary_list = []
        for name, data in parsed_data.items():
            mat = st.session_state.materials.get(name, list(U_VALUES.keys())[0])
            u_val = U_VALUES[mat]
            
            delta_t = abs(data['avg'] - env_temp)
            heat_loss = delta_t * u_val * 1.0 
            
            summary_list.append({
                "Subtab Name": name,
                "Average Temp (°C)": data['avg'],
                "Material": mat,
                "U-Value": u_val,
                "Heat Loss (W/m²)": heat_loss
            })
            
        df = pd.DataFrame(summary_list)
        
        mean_hl = df["Heat Loss (W/m²)"].mean()
        sigma_hl = df["Heat Loss (W/m²)"].std()
        
        if pd.isna(sigma_hl):
            sigma_hl = 0
            
        def assign_severity(hl):
            if hl < (mean_hl - 0.5 * sigma_hl):
                return "Low"
            elif hl > (mean_hl + 0.5 * sigma_hl):
                return "High"
            else:
                return "Medium"
                
        df["Severity"] = df["Heat Loss (W/m²)"].apply(assign_severity)
        
        # --- Histogram Chart ---
        color_discrete_map = {
            "Low": "#85C1E9",    
            "Medium": "#82E0AA", 
            "High": "#F1948A"    
        }
        
        fig = px.histogram(
            df, 
            x="Heat Loss (W/m²)", 
            color="Severity",
            color_discrete_map=color_discrete_map,
            nbins=10, 
            title="Distribution of Heat Loss Locations",
            barmode="group"  
        )
        
        fig.update_layout(
            yaxis_title="Count of Locations",
            bargap=0.15 
        )
        
        fig.add_vline(
            x=mean_hl, 
            line_dash="dash", 
            line_color="black", 
            annotation_text=f"Average: {mean_hl:.2f}", 
            annotation_position="top right"
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # --- Color-coded Table ---
        def highlight_rows(row):
            if row['Severity'] == 'Low':
                color = 'rgba(133, 193, 233, 0.3)'  
            elif row['Severity'] == 'Medium':
                color = 'rgba(130, 224, 170, 0.3)'  
            elif row['Severity'] == 'High':
                color = 'rgba(241, 148, 138, 0.3)'  
            else:
                color = ''
            return [f'background-color: {color}'] * len(row)
        
        styled_df = (df.style
                     .apply(highlight_rows, axis=1)
                     .set_properties(**{'font-size': '16px', 'padding': '10px'})) 
        
        st.dataframe(styled_df, use_container_width=True)
        
        st.markdown("### Overall Statistics")
        st.metric(label="Average Heat Loss Across All Locations", value=f"{mean_hl:.2f} W/m²")

# --- INDIVIDUAL SUBTABS ---
else:
    data = parsed_data[selected_tab]
    st.title(f"Details: {selected_tab}")
    
    image = Image.open(data["file"])

    aspect_ratio = image.width / image.height
    new_width = int(400 * aspect_ratio)
    resized_image = image.resize((new_width, 400))

    st.image(resized_image, caption=data["original_name"])
    
    st.markdown("### Temperature Data")
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Temperature", f"{data['avg']} °C")
    col2.metric("Max Temperature", f"{data['max']} °C")
    col3.metric("Min Temperature", f"{data['min']} °C")
    
    st.markdown("---")
    
    st.markdown("### Material & Heat Loss Calculation")
    
    current_mat = st.session_state.materials.get(selected_tab, list(U_VALUES.keys())[0])
    mat_index = list(U_VALUES.keys()).index(current_mat)
    
    selected_mat = st.selectbox(
        "Select Material for this area", 
        options=list(U_VALUES.keys()), 
        index=mat_index
    )
    
    st.session_state.materials[selected_tab] = selected_mat
    
    u_val = U_VALUES[selected_mat]
    delta_t = abs(data['avg'] - env_temp)
    heat_loss = delta_t * u_val * 1.0 
    
    st.info(f"**U-Value:** {u_val}  |  **|ΔT|:** {delta_t:.2f} °C")
    st.success(f"**Calculated Heat Loss (per 1m²):** {heat_loss:.2f} W")