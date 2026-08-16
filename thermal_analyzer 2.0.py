import streamlit as st
import pandas as pd
import numpy as np
import re
from PIL import Image, ImageOps
import plotly.express as px
import plotly.graph_objects as go
import io

# ── Material definitions ────────────────────────────────────────────────────
#("material name, the thermal constant of a certain material");
MATERIALS = {
    1:  ("Single Glazed Glass",       5.7),
    2:  ("Double Glazed Glass",        2.8),
    3:  ("Steel",                      5.7),
    4:  ("Concrete",                   3.0),
    5:  ("Vent Polymer (ABS/PVC)",     3.0),
    6:  ("PVC Single Glazed",          4.8),
    7:  ("PVC Double Glazed",          2.8),
    8:  ("PVC Triple Glazed",          2.1),
    9:  ("Solid Wood Door",            3.0),
    10: ("Glazed Wood Single",         5.7),
    11: ("Glazed Wood Double",         3.4),
    12: ("Glazed Wood Triple",         2.6),
    13: ("Metal Single",               5.7),
    14: ("Metal Double",               3.4),
    15: ("Metal Triple",               2.6),
    16: ("Solid Brick",                2.1),
    17: ("Solid Brick Insulated",      0.28),
    18: ("Solid Stone",                2.25),
    19: ("Solid Stone Insulated",      0.32),
    20: ("Solid Concrete",             3.0),
    21: ("Solid Concrete Insulated",   0.31),
    22: ("Cavity Wall Uninsulated",    1.3),
    23: ("Cavity Wall Insulated",      0.55),
    24: ("Hardwood",                   0.18),
    25: ("Softwood",                   0.13),
    26: ("Plasterboard",               0.16),
}

U_VALUES   = {name: u for _, (name, u) in MATERIALS.items()}
ID_TO_NAME = {id_: name for id_, (name, _) in MATERIALS.items()}

# ── Constants ────────────────────────────────────────────────────────────────
HOURS_PER_YEAR     = 8760

# ── Session state defaults ──────────────────────────────────────────────────
for key, default in [
    ("materials",  {}),
    ("areas",      {}),
    ("notes",      {}),
    ("custom_u",   {}),
    ("flagged",    {}),   # NEW: flag zones for action
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="Thermal Image Analyzer")

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Space Mono', monospace !important; }

    [data-testid="stMetricValue"] {
        font-family: 'Space Mono', monospace !important;
        font-size: 1.6rem !important;
    }

    .badge-high   { background:#F1948A; color:#fff; padding:2px 10px; border-radius:12px; font-weight:600; font-size:0.8rem; }
    .badge-medium { background:#82E0AA; color:#333; padding:2px 10px; border-radius:12px; font-weight:600; font-size:0.8rem; }
    .badge-low    { background:#85C1E9; color:#fff; padding:2px 10px; border-radius:12px; font-weight:600; font-size:0.8rem; }
    .badge-flag   { background:#F39C12; color:#fff; padding:2px 10px; border-radius:12px; font-weight:600; font-size:0.8rem; }

    .info-box {
        background: rgba(130,224,170,0.15);
        border-left: 4px solid #82E0AA;
        border-radius: 6px;
        padding: 10px 16px;
        margin: 8px 0;
        font-size: 0.95rem;
    }
    .warn-box {
        background: rgba(241,148,138,0.15);
        border-left: 4px solid #F1948A;
        border-radius: 6px;
        padding: 10px 16px;
        margin: 8px 0;
        font-size: 0.95rem;
    }
    .flag-box {
        background: rgba(243,156,18,0.15);
        border-left: 4px solid #F39C12;
        border-radius: 6px;
        padding: 10px 16px;
        margin: 8px 0;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("Settings")

with st.sidebar.expander("Material ID Reference", expanded=False):
    st.dataframe(
        pd.DataFrame({"ID": list(ID_TO_NAME.keys()), "Material": list(ID_TO_NAME.values())}).set_index("ID")
    )

env_temp = st.sidebar.number_input("Environmental Temperature (°C)", value=20.0, step=0.1)

uploaded_files = st.sidebar.file_uploader(
    "Upload Thermal Images (Max 20)",
    accept_multiple_files=True,
    type=["png", "jpg", "jpeg"],
)
if len(uploaded_files) > 20:
    st.sidebar.warning("Maximum 20 files. Only processing the first 20.")
    uploaded_files = uploaded_files[:20]

# ── Parse filenames ──────────────────────────────────────────────────────────
parsed_data = {}
pattern = r"^(.*?)\(([-+]?\d*\.?\d+)\s+([-+]?\d*\.?\d+)\s+([-+]?\d*\.?\d+)\s+(\d+)\)(?:\.[a-zA-Z0-9]+)?$"

for file in uploaded_files:
    match = re.match(pattern, file.name)
    if match:
        name, avg_t, max_t, min_t, mat_id = match.groups()
        mat_id   = int(mat_id)
        mat_name = ID_TO_NAME.get(mat_id, list(U_VALUES.keys())[0])

        parsed_data[name] = {
            "file": file,
            "avg":  float(avg_t),
            "max":  float(max_t),
            "min":  float(min_t),
            "original_name": file.name,
        }

        if name not in st.session_state.materials:
            st.session_state.materials[name] = mat_name
        if name not in st.session_state.areas:
            st.session_state.areas[name] = 1.0
        if name not in st.session_state.notes:
            st.session_state.notes[name] = ""
        if name not in st.session_state.custom_u:
            st.session_state.custom_u[name] = None
        if name not in st.session_state.flagged:
            st.session_state.flagged[name] = False
    else:
        st.sidebar.error(f"Invalid format: {file.name}")

# ── Helper: compute heat loss row ─────────────────────────────────────────────
def compute_zone(name, data, env_temp):
    mat    = st.session_state.materials.get(name, list(U_VALUES.keys())[0])
    area   = st.session_state.areas.get(name, 1.0)
    cu     = st.session_state.custom_u.get(name)
    u_val  = cu if cu else U_VALUES[mat]
    delta_t          = abs(data["avg"] - env_temp)
    heat_loss_per_m2 = delta_t * u_val
    total_heat_loss  = heat_loss_per_m2 * area
    annual_kwh       = (total_heat_loss * HOURS_PER_YEAR) / 1000.0
    return mat, area, u_val, delta_t, heat_loss_per_m2, total_heat_loss, annual_kwh

# ── Navigation ───────────────────────────────────────────────────────────────
tabs = ["Overview"] + list(parsed_data.keys())
selected_tab = st.sidebar.radio("Navigate", tabs)

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  OVERVIEW                                                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝
if selected_tab == "Overview":
    st.title("Thermal Analysis Overview")

    if not parsed_data:
        st.info("Upload thermal images via the sidebar to get started.")
        st.stop()

    # ── Build summary dataframe ─────────────────────────────────────────────
    summary_list = []
    for name, data in parsed_data.items():
        mat, area, u_val, delta_t, hl_m2, hl_total, ann_kwh = compute_zone(name, data, env_temp)
        summary_list.append({
            "Zone":                name,
            "Avg Temp (°C)":       data["avg"],
            "Material":            mat,
            "U-Value (W/m²K)":     u_val,
            "Area (m²)":           area,
            "Heat Loss (W/m²)":    round(hl_m2, 2),
            "Total Heat Loss (W)": round(hl_total, 2),
            "Annual kWh":          round(ann_kwh, 1),
            "Flagged":             st.session_state.flagged.get(name, False),
            "Notes":               st.session_state.notes.get(name, ""),
        })

    df = pd.DataFrame(summary_list)

    mean_hl  = df["Total Heat Loss (W)"].mean()
    sigma_hl = df["Total Heat Loss (W)"].std()
    if pd.isna(sigma_hl):
        sigma_hl = 0

    def assign_severity(hl):
        if hl < (mean_hl - 0.5 * sigma_hl):
            return "Low"
        elif hl > (mean_hl + 0.5 * sigma_hl):
            return "High"
        else:
            return "Medium"

    df["Severity"] = df["Total Heat Loss (W)"].apply(assign_severity)

    # ── Controls: sort + filter ─────────────────────────────────────────────
    st.subheader("Thermal Analysis Summary")
    ctrl1, ctrl2, ctrl3 = st.columns(3)
    with ctrl1:
        severity_filter = st.multiselect(
            "Filter by Severity",
            options=["High", "Medium", "Low"],
            default=["High", "Medium", "Low"],
        )
    with ctrl2:
        sort_col = st.selectbox(
            "Sort by",
            options=["Total Heat Loss (W)", "Heat Loss (W/m²)", "Avg Temp (°C)", "Annual kWh", "Zone"],
            index=0,
        )
    with ctrl3:
        sort_asc = st.radio("Order", ["Descending ↓", "Ascending ↑"], horizontal=True) == "Ascending ↑"

    # FIX: sort on the raw numeric/string column BEFORE any categorical casting
    df_filtered = (
        df[df["Severity"].isin(severity_filter)]
        .sort_values(sort_col, ascending=sort_asc)
        .reset_index(drop=True)
    )

    # ── Top N worst zones ───────────────────────────────────────────────────
    top_n = min(3, len(df))
    worst = df.nlargest(top_n, "Total Heat Loss (W)")
    if not worst.empty:
        st.markdown("#### ⚠️ Worst Offenders")
        wo_cols = st.columns(top_n)
        for i, (_, row) in enumerate(worst.iterrows()):
            with wo_cols[i]:
                st.markdown(
                    f"""<div class="warn-box">
                        <b>{row['Zone']}</b><br>
                        {row['Total Heat Loss (W)']:.1f} W total<br>
                        {row['Annual kWh']:.1f} kWh/yr estimated<br>
                        <small>{row['Material']}</small>
                    </div>""",
                    unsafe_allow_html=True,
                )

    # ── Flagged zones callout ───────────────────────────────────────────────
    flagged_zones = df[df["Flagged"] == True]
    if not flagged_zones.empty:
        st.markdown("#### 🚩 Flagged for Action")
        flag_cols = st.columns(min(3, len(flagged_zones)))
        for i, (_, row) in enumerate(flagged_zones.iterrows()):
            with flag_cols[i % 3]:
                st.markdown(
                    f'<div class="flag-box"><b>{row["Zone"]}</b> — {row["Total Heat Loss (W)"]:.1f} W</div>',
                    unsafe_allow_html=True,
                )

    # ── Charts ──────────────────────────────────────────────────────────────
    color_map = {"Low": "#85C1E9", "Medium": "#82E0AA", "High": "#F1948A"}

    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Bar Chart by Zone", "Distribution Histogram", "Radar Chart"])

    with chart_tab1:
        fig_bar = px.bar(
            df_filtered.sort_values("Total Heat Loss (W)", ascending=True),
            x="Total Heat Loss (W)",
            y="Zone",
            color="Severity",
            color_discrete_map=color_map,
            orientation="h",
            title="Total Heat Loss by Zone",
            text="Total Heat Loss (W)",
        )
        fig_bar.update_traces(texttemplate="%{text:.1f} W", textposition="outside")
        fig_bar.update_layout(yaxis_title="", xaxis_title="Total Heat Loss (W)", showlegend=True)
        st.plotly_chart(fig_bar, use_container_width=True)

    with chart_tab2:
        fig_hist = px.histogram(
            df_filtered,
            x="Heat Loss (W/m²)",
            color="Severity",
            color_discrete_map=color_map,
            nbins=8,
            barmode="group",
            title="Distribution of Heat Loss per m²",
        )
        fig_hist.update_layout(yaxis_title="Count of Locations", bargap=0.05)
        fig_hist.add_vline(
            x=mean_hl,
            line_dash="dash",
            line_color="black",
            annotation_text=f"Avg: {mean_hl:.2f}",
            annotation_position="top right",
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with chart_tab3:
        # Radar chart: compare zones across normalised metrics
        if len(df_filtered) >= 3:
            radar_cols = ["Heat Loss (W/m²)", "U-Value (W/m²K)", "Avg Temp (°C)", "Annual kWh"]
            # Normalise each column to 0-1
            radar_df = df_filtered[["Zone"] + radar_cols].copy()
            for col in radar_cols:
                col_min = radar_df[col].min()
                col_max = radar_df[col].max()
                denom = (col_max - col_min) if (col_max - col_min) != 0 else 1
                radar_df[col] = (radar_df[col] - col_min) / denom

            fig_radar = go.Figure()
            for _, row in radar_df.iterrows():
                values = [row[c] for c in radar_cols] + [row[radar_cols[0]]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=radar_cols + [radar_cols[0]],
                    fill="toself",
                    name=row["Zone"],
                    opacity=0.6,
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title="Zone Comparison (Normalised Metrics)",
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("Upload at least 3 zones to see the radar chart.")

    # ── Styled table ────────────────────────────────────────────────────────
    def highlight_rows(row):
        c = {"Low": "rgba(133,193,233,0.3)", "Medium": "rgba(130,224,170,0.3)", "High": "rgba(241,148,138,0.3)"}.get(row["Severity"], "")
        return [f"background-color: {c}"] * len(row)

    display_cols = ["Zone", "Avg Temp (°C)", "Material", "U-Value (W/m²K)", "Area (m²)",
                    "Heat Loss (W/m²)", "Total Heat Loss (W)", "Annual kWh", "Severity", "Flagged"]
    styled = (
        df_filtered[display_cols].style
        .apply(highlight_rows, axis=1)
        .set_properties(**{"font-size": "15px", "padding": "8px"})
    )
    st.dataframe(styled, use_container_width=True)

    # ── Overall stats ───────────────────────────────────────────────────────
    st.markdown("### Overall Statistics")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Avg Heat Loss",       f"{df['Heat Loss (W/m²)'].mean():.2f} W/m²")
    m2.metric("Total Heat Loss",     f"{df['Total Heat Loss (W)'].sum():.1f} W")
    m3.metric("Annual Energy Lost",  f"{df['Annual kWh'].sum():,.1f} kWh/yr")
    m4.metric("Worst Zone",          df.loc[df['Total Heat Loss (W)'].idxmax(), 'Zone'])
    m5.metric("Best Zone",           df.loc[df['Total Heat Loss (W)'].idxmin(), 'Zone'])

    # ── CSV Export ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Export Report")

    export_cols = ["Zone", "Avg Temp (°C)", "Material", "U-Value (W/m²K)", "Area (m²)",
                   "Heat Loss (W/m²)", "Total Heat Loss (W)", "Annual kWh",
                   "Severity", "Flagged", "Notes"]
    csv_bytes = df[export_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Full Report as CSV",
        data=csv_bytes,
        file_name="thermal_analysis_report.csv",
        mime="text/csv",
    )

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  INDIVIDUAL ZONE SUBTAB                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝
else:
    data = parsed_data[selected_tab]

    mat, area, u_val, delta_t, heat_loss_per_m2, total_heat_loss, annual_kwh = compute_zone(
        selected_tab, data, env_temp
    )

    # Severity relative to all zones
    all_totals = []
    for n, d in parsed_data.items():
        _, _, _, _, _, hl, _ = compute_zone(n, d, env_temp)
        all_totals.append(hl)
    mean_all  = np.mean(all_totals)
    sigma_all = np.std(all_totals) if len(all_totals) > 1 else 0

    if total_heat_loss < (mean_all - 0.5 * sigma_all):
        severity, badge_class = "Low", "badge-low"
    elif total_heat_loss > (mean_all + 0.5 * sigma_all):
        severity, badge_class = "High", "badge-high"
    else:
        severity, badge_class = "Medium", "badge-medium"

    st.title(f"{selected_tab}")

    # Severity + flag badge on the same row
    flag_state = st.session_state.flagged.get(selected_tab, False)
    badge_html = f'<span class="{badge_class}">{severity} Severity</span>'
    if flag_state:
        badge_html += '&nbsp;<span class="badge-flag">🚩 Flagged for Action</span>'
    st.markdown(badge_html, unsafe_allow_html=True)
    st.markdown("")

    # ── Image ───────────────────────────────────────────────────────────────
    image = ImageOps.exif_transpose(Image.open(data["file"]))
    ar    = image.width / image.height
    st.image(image.resize((int(400 * ar), 400)), caption=data["original_name"])

    # ── Temperature metrics ─────────────────────────────────────────────────
    st.markdown("### Temperature Data")
    c1, c2, c3 = st.columns(3)
    c1.metric("Average Temperature", f"{data['avg']} °C")
    c2.metric("Max Temperature",     f"{data['max']} °C")
    c3.metric("Min Temperature",     f"{data['min']} °C")

    st.markdown("---")

    # ── Material & area inputs ──────────────────────────────────────────────
    st.markdown("### Material & Area")
    col_mat, col_area = st.columns(2)

    with col_mat:
        current_mat  = st.session_state.materials.get(selected_tab, list(U_VALUES.keys())[0])
        mat_index    = list(U_VALUES.keys()).index(current_mat)
        selected_mat = st.selectbox("Material", options=list(U_VALUES.keys()), index=mat_index)
        st.session_state.materials[selected_tab] = selected_mat

    with col_area:
        area_input = st.number_input(
            "Zone Area (m²)",
            min_value=0.01,
            value=float(st.session_state.areas.get(selected_tab, 1.0)),
            step=0.1,
            format="%.2f",
        )
        st.session_state.areas[selected_tab] = area_input

    # ── Custom U-value override ─────────────────────────────────────────────
    st.markdown("### Custom U-Value Override")
    use_custom = st.checkbox(
        "Override U-value with a custom value",
        value=(st.session_state.custom_u.get(selected_tab) is not None),
    )
    if use_custom:
        current_custom = st.session_state.custom_u.get(selected_tab) or U_VALUES[selected_mat]
        custom_u_input = st.number_input(
            "Custom U-Value (W/m²K)",
            min_value=0.01,
            value=float(current_custom),
            step=0.01,
            format="%.3f",
        )
        st.session_state.custom_u[selected_tab] = custom_u_input
        u_val = custom_u_input
    else:
        st.session_state.custom_u[selected_tab] = None
        u_val = U_VALUES[selected_mat]

    # Recalculate with latest inputs
    delta_t          = abs(data["avg"] - env_temp)
    heat_loss_per_m2 = delta_t * u_val
    total_heat_loss  = heat_loss_per_m2 * area_input
    annual_kwh       = (total_heat_loss * HOURS_PER_YEAR) / 1000.0

    # ── Heat loss results ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Heat Loss Calculation")

    st.markdown(
        f'<div class="info-box">'
        f'<b>U-Value:</b> {u_val:.3f} W/m²K &nbsp;|&nbsp; '
        f'<b>|ΔT|:</b> {delta_t:.2f} °C &nbsp;|&nbsp; '
        f'<b>Area:</b> {area_input:.2f} m²'
        f'</div>',
        unsafe_allow_html=True,
    )

    r1, r2, r3 = st.columns(3)
    r1.metric("Heat Loss per m²",  f"{heat_loss_per_m2:.2f} W/m²")
    r2.metric("Total Heat Loss",   f"{total_heat_loss:.2f} W")
    r3.metric("Annual Energy Lost", f"{annual_kwh:.1f} kWh/yr")

    # Contextual callout
    if severity == "High":
        st.markdown(
            f'<div class="warn-box">This zone\'s heat loss is '
            f'<b>{total_heat_loss - mean_all:.1f} W above average</b>. '
            f'Consider improving insulation or replacing the glazing.</div>',
            unsafe_allow_html=True,
        )
    elif severity == "Low":
        st.markdown(
            f'<div class="info-box">This zone performs '
            f'<b>{mean_all - total_heat_loss:.1f} W below average</b> — well insulated.</div>',
            unsafe_allow_html=True,
        )

    # ── Flag for action ─────────────────────────────────────────────────────
    st.markdown("---")
    flag_checked = st.checkbox(
        "🚩 Flag this zone for action",
        value=st.session_state.flagged.get(selected_tab, False),
        help="Flagged zones are highlighted in the Overview summary.",
    )
    st.session_state.flagged[selected_tab] = flag_checked

    # ── Notes ───────────────────────────────────────────────────────────────
    st.markdown("### Notes")
    note_input = st.text_area(
        "Add observations or recommendations for this zone",
        value=st.session_state.notes.get(selected_tab, ""),
        height=120,
        placeholder="e.g. Visible condensation on lower pane. Recommend resealing frame.",
    )
    st.session_state.notes[selected_tab] = note_input
