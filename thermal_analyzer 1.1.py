import streamlit as st
import pandas as pd
import numpy as np
import re
from PIL import Image, ImageOps 
import plotly.express as px

# 1. 给每种材质分配唯一的数字 ID
MATERIALS = {
    1: ("Single Glazed Glass", 5.7),
    2: ("Double Glazed Glass", 2.8),
    3: ("Steel", 5.7),
    4: ("Concrete", 3.0),
    5: ("Vent Polymer (ABS/PVC)", 3.0),
    6: ("PVC Single Glazed", 4.8), 
    7: ("PVC Double Glazed", 2.8), 
    8: ("PVC Triple Glazed", 2.1),
    9: ("Solid Wood Door", 3.0), 
    10: ("Glazed Wood Single", 5.7), 
    11: ("Glazed Wood Double", 3.4),
    12: ("Glazed Wood Triple", 2.6), 
    13: ("Metal Single", 5.7), 
    14: ("Metal Double", 3.4), 
    15: ("Metal Triple", 2.6),
    16: ("Solid Brick", 2.1), 
    17: ("Solid Brick Insulated", 0.28), 
    18: ("Solid Stone", 2.25),
    19: ("Solid Stone Insulated", 0.32), 
    20: ("Solid Concrete", 3.0), 
    21: ("Solid Concrete Insulated", 0.31),
    22: ("Cavity Wall Uninsulated", 1.3), 
    23: ("Cavity Wall Insulated", 0.55), 
    24: ("Hardwood", 0.18),
    25: ("Softwood", 0.13), 
    26: ("Plasterboard", 0.16)
}

# 辅助字典，保证后续代码逻辑不变
U_VALUES = {name: u_val for id, (name, u_val) in MATERIALS.items()}
ID_TO_NAME = {id: name for id, (name, u_val) in MATERIALS.items()}

# 2. Initialize session state
if 'materials' not in st.session_state:
    st.session_state.materials = {}
if 'main_images_cache' not in st.session_state:
    st.session_state.main_images_cache = []

# Set page layout
st.set_page_config(layout="wide", page_title="Thermal Image Analyzer")

# --- SIDEBAR & GLOBAL SETTINGS ---
st.sidebar.title("Settings & Navigation")

# 在侧边栏显示材质编号对照表，方便你随时查看
with st.sidebar.expander("Show Material ID Reference", expanded=False):
    st.dataframe(pd.DataFrame({
        "ID": list(ID_TO_NAME.keys()),
        "Material": list(ID_TO_NAME.values())
    }).set_index("ID"))

env_temp = st.sidebar.number_input("Environmental Temperature (°C)", value=20.0, step=0.1)

uploaded_files = st.sidebar.file_uploader(
    "Upload Thermal Images (Max 20)", 
    accept_multiple_files=True, 
    type=['png', 'jpg', 'jpeg']
)

if len(uploaded_files) > 20:
    st.sidebar.warning("Maximum 20 files allowed. Only processing the first 20.")
    uploaded_files = uploaded_files[:20]

# 3. Parse filenames 
parsed_data = {}
# 修改正则：匹配 Name(avg max min id)
pattern = r"^(.*?)\(([-+]?\d*\.?\d+)\s+([-+]?\d*\.?\d+)\s+([-+]?\d*\.?\d+)\s+(\d+)\)(?:\.[a-zA-Z0-9]+)?$"

for file in uploaded_files:
    match = re.match(pattern, file.name)
    if match:
        name, avg_t, max_t, min_t, mat_id = match.groups()
        mat_id = int(mat_id)
        
        # 匹配编号获取材质名称。如果编号写错了（比如写了99），则默认使用第一个材质
        mat_name = ID_TO_NAME.get(mat_id, list(U_VALUES.keys())[0])
        
        parsed_data[name] = {
            "file": file,
            "avg": float(avg_t),
            "max": float(max_t),
            "min": float(min_t),
            "original_name": file.name
        }
        
        # 关键更新：将读取到的材质自动存入缓存，这样下拉菜单就会自动选中它
        if name not in st.session_state.materials:
            st.session_state.materials[name] = mat_name
            
    else:
        st.sidebar.error(f"Invalid format: {file.name}. Expected: Name(avg max min id)")

# 4. Navigation
tabs = ["Overview"] + list(parsed_data.keys())
selected_tab = st.sidebar.radio("Navigation Menu", tabs)

# --- Overview ---
if selected_tab == "Overview":
    st.title("Overview")
    
    st.subheader("Main Entrance & Thermal Images")
    
    main_images = st.file_uploader(
        "Upload Main Entrance and Thermal Image (Select up to 2 files)", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True, 
        key="main_imgs"
    )
    
    if main_images:
        if len(main_images) > 2:
            st.warning("You uploaded more than 2 files. Only keeping the first two.")
            
        new_cache = []
        for file in main_images[:2]:
            img = Image.open(file)
            img = ImageOps.exif_transpose(img) 
            new_cache.append(img)
        st.session_state.main_images_cache = new_cache

    if st.session_state.main_images_cache:
        if st.button("Clear Main Images"):
            st.session_state.main_images_cache = []
            st.rerun() 
            
        spacer_left, col1, col2, spacer_right = st.columns([0.15, 0.35, 0.35, 0.15])
        
        cache = st.session_state.main_images_cache
        if len(cache) >= 1:
            with col1:
                st.caption("Main Entrance Photo")
                st.image(cache[0], use_container_width=True)
        if len(cache) >= 2:
            with col2:
                st.caption("Main Thermal Image")
                st.image(cache[1], use_container_width=True)

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
            nbins=8, 
            title="Distribution of Heat Loss Locations",
            barmode="group"
        )
        
        fig.update_layout(
            yaxis_title="Count of Locations",
            bargap=0.05 
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
    image = ImageOps.exif_transpose(image) 

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