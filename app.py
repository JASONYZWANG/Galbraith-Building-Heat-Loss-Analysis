"""Streamlit interface for the Galbraith thermal screening prototype."""
from dataclasses import replace
import hashlib
import io
from pathlib import Path

import pandas as pd
from PIL import Image, ImageOps, UnidentifiedImageError
import plotly.express as px
import streamlit as st

from thermal_analysis.model import analyze, export_csv, parse_filename, read_csv

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Galbraith Thermal Analysis", layout="wide")
st.title("Galbraith Thermal Analysis")
st.caption("APS112 · Team 021 · Mobile Thermal Imaging System")
st.info("Compare surface-temperature screening indicators. These values are not calibrated building heat-flow measurements or verified energy savings.")

source = st.sidebar.radio("Data source", ["Example observations", "Upload CSV", "Upload labelled images"])
hours = st.sidebar.number_input("Constant-condition scenario hours", min_value=0.0, max_value=8760.0, value=0.0, step=100.0)
st.sidebar.caption("Optional extrapolation at unchanged conditions; not an annual energy forecast.")
images = {}
try:
    if source == "Example observations":
        payload = (ROOT / "data/example_observations.csv").read_bytes()
        zones = read_csv(payload.decode("utf-8"))
        st.caption("Three historical observations; 22.5°C indoor reference and assumed 1 m² areas. See docs/data-provenance.md.")
    elif source == "Upload CSV":
        upload = st.sidebar.file_uploader("Observation CSV", type=["csv"])
        if upload is None:
            st.write("Upload a CSV using the example file's column names.")
            st.stop()
        payload = upload.getvalue()
        if len(payload) > 2_000_000:
            raise ValueError("CSV must be smaller than 2 MB.")
        zones = read_csv(payload.decode("utf-8-sig"))
    else:
        reference = st.sidebar.number_input("Reference temperature (°C)", min_value=-273.15, value=22.5)
        basis = st.sidebar.selectbox("Reference basis", ["indoor_air", "outdoor_air", "other"])
        uploads = st.sidebar.file_uploader("Images: Zone(avg max min ID).jpg", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        st.sidebar.caption("IDs: 1 = single glass, 2 = double glass, 3 = metal edge. Other materials: use CSV.")
        if not uploads:
            st.write("Upload labelled images. Temperatures are read from filenames, not image pixels.")
            st.stop()
        if len(uploads) > 20:
            raise ValueError("Upload at most 20 images.")
        zones, parts, names = [], [], set()
        for upload in uploads:
            zone = parse_filename(upload.name, reference, basis)
            if zone.zone.casefold() in names:
                raise ValueError("Duplicate zone names. Give each observation a distinct name.")
            names.add(zone.zone.casefold())
            raw = upload.getvalue()
            if len(raw) > 10_000_000:
                raise ValueError("Each image must be smaller than 10 MB.")
            with Image.open(io.BytesIO(raw)) as im:
                im.verify()
            images[zone.zone] = raw
            zones.append(zone)
            parts.append(upload.name.encode() + raw)
        payload = b"".join(parts) + f"{reference}:{basis}".encode()
except (ValueError, UnicodeDecodeError, OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
    st.error(str(exc))
    st.stop()

# Stable per-dataset state avoids leaking edits between uploads with matching names.
dataset_id = hashlib.sha256(source.encode() + payload).hexdigest()
if st.session_state.get("dataset_id") != dataset_id:
    st.session_state.dataset_id = dataset_id
    st.session_state.edits = {}

selected = st.selectbox("Inspect or edit a zone", [z.zone for z in zones])
base = next(z for z in zones if z.zone == selected)
current = replace(base, **st.session_state.edits.get(selected, {}))
with st.expander("Zone assumptions and observations", expanded=True):
    with st.form(f"edit-{dataset_id}-{selected}"):
        left, middle, right = st.columns(3)
        material = left.text_input("Material / assembly label", current.material)
        u_value = middle.number_input("Assumed U-value (W/m²K)", min_value=0.001, value=current.u_value, format="%.3f")
        area = right.number_input("Area (m²)", min_value=0.001, value=current.area_m2, format="%.3f")
        note = st.text_area("Observation notes", current.note)
        flagged = st.checkbox("Flag for further inspection", value=st.session_state.get(f"flag-{dataset_id}-{selected}", False))
        if st.form_submit_button("Apply changes"):
            try:
                replace(current, material=material, u_value=u_value, area_m2=area, note=note)
                st.session_state.edits[selected] = dict(material=material, u_value=u_value, area_m2=area, note=note)
                st.session_state[f"flag-{dataset_id}-{selected}"] = flagged
            except ValueError as exc:
                st.error(str(exc))

try:
    rows = [analyze(replace(z, **st.session_state.edits.get(z.zone, {})), hours) for z in zones]
except ValueError as exc:
    st.error(str(exc))
    st.stop()
for row in rows:
    row["flagged"] = st.session_state.get(f"flag-{dataset_id}-{row['zone']}", False)
df = pd.DataFrame(rows)
detail = next(row for row in rows if row["zone"] == selected)
a, b, c = st.columns(3)
a.metric("Selected zone indicator", f"{detail['proxy_w_m2']:.2f} W/m²")
b.metric("Area-scaled indicator", f"{detail['proxy_w']:.2f} W")
c.metric("Screening band", detail["severity"])
st.caption("Low < 10 · Medium 10–50 · High > 50 W/m². Project-specific bands, applied before rounding.")
if selected in images:
    with Image.open(io.BytesIO(images[selected])) as im:
        st.image(ImageOps.exif_transpose(im), caption=selected, width=500)
if len({(z.reference_basis, z.reference_c) for z in zones}) > 1:
    st.warning("References differ across observations. Rankings may reflect different conditions as well as surface differences.")

st.subheader("Compare zones")
left, right = st.columns(2)
bands = left.multiselect("Show screening bands", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])
sort_by = right.selectbox("Rank by", ["proxy_w_m2", "proxy_w", "zone"])
filtered = df[df.severity.isin(bands)].sort_values(sort_by, ascending=sort_by == "zone")
colors = {"Low": "#3984a8", "Medium": "#cf8a23", "High": "#bb4545"}
if filtered.empty:
    st.info("No observations match the selected bands.")
else:
    fig = px.bar(filtered, x="proxy_w_m2", y="zone", color="severity", orientation="h",
                 color_discrete_map=colors, labels={"proxy_w_m2": "Screening indicator (W/m²)", "zone": "Zone", "severity": "Band"})
    fig.update_layout(yaxis={"categoryorder": "array", "categoryarray": filtered.zone.tolist()[::-1]})
    st.plotly_chart(fig, width="stretch")
    st.dataframe(filtered, hide_index=True, width="stretch")
st.caption("The table and chart follow the filter. Export includes every observation and its assumptions. Edits are held only in this browser session.")
st.download_button("Download complete analysis CSV", export_csv(rows), "galbraith_analysis.csv", "text/csv")
if hours:
    st.caption(f"Scenario column = area-scaled indicator × {hours:g} hours / 1000. No weather, infiltration or HVAC model is included.")
with st.expander("How to interpret the result"):
    st.write("The prototype uses U × |surface temperature − reference temperature| as a screening proxy, then multiplies by area. A cold surface or a high band is a reason to investigate; it does not establish actual heat flow, insulation quality or a retrofit saving. Reflections, emissivity, mixed materials and reference conditions can affect the result.")
