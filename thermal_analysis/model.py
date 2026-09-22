"""Surface-temperature screening proxy, not a calibrated envelope heat-flow model."""
import csv
from dataclasses import asdict, dataclass
import io
import math
import re


# Retained identifiers for the three consistent historical demonstration records.
# These are inherited project assumptions, not measured assembly U-values.
MATERIALS = {
    1: ("Single glazed glass", 5.7),
    2: ("Double glazed glass", 2.8),
    3: ("Metal door edge", 5.7),
}


@dataclass(frozen=True)
class Zone:
    zone: str
    average_c: float
    maximum_c: float
    minimum_c: float
    material: str
    u_value: float
    area_m2: float
    reference_c: float
    reference_basis: str
    note: str = ""

    def __post_init__(self):
        for key in ("average_c", "maximum_c", "minimum_c", "u_value", "area_m2", "reference_c"):
            value = getattr(self, key)
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{key} must be a finite number.")
        if not self.zone.strip() or not self.material.strip():
            raise ValueError("Zone and material names are required.")
        if self.reference_basis not in ("indoor_air", "outdoor_air", "other"):
            raise ValueError("reference_basis must be indoor_air, outdoor_air or other.")
        if not self.minimum_c <= self.average_c <= self.maximum_c:
            raise ValueError("Temperatures must satisfy minimum <= average <= maximum.")
        if min(self.minimum_c, self.reference_c) < -273.15:
            raise ValueError("Temperature cannot be below absolute zero.")
        if self.u_value <= 0 or self.area_m2 <= 0:
            raise ValueError("U-value and area must be greater than zero.")


def severity(density):
    """Project-specific fixed bands; 10 and 50 belong to Medium."""
    if not math.isfinite(density) or density < 0:
        raise ValueError("Density must be finite and nonnegative.")
    return "Low" if density < 10 else "Medium" if density <= 50 else "High"


def analyze(zone, hours=0.0):
    if not math.isfinite(hours) or not 0 <= hours <= 8760:
        raise ValueError("Scenario hours must be between 0 and 8760.")
    delta = abs(zone.average_c - zone.reference_c)
    density = zone.u_value * delta
    total = density * zone.area_m2
    energy = total * hours / 1000
    if not all(math.isfinite(v) for v in (delta, density, total, energy)):
        raise ValueError("Inputs produce an out-of-range result.")
    return {**asdict(zone), "temperature_difference_k": delta,
            "proxy_w_m2": density, "proxy_w": total,
            "severity": severity(density), "scenario_hours": hours,
            "scenario_kwh": energy}


def read_csv(text):
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
    required = set(Zone.__dataclass_fields__) - {"note"}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError("Missing CSV columns: " + ", ".join(sorted(required - set(reader.fieldnames or []))))
    zones, names = [], set()
    numeric = {"average_c", "maximum_c", "minimum_c", "u_value", "area_m2", "reference_c"}
    for number, row in enumerate(reader, 2):
        try:
            args = {key: float(row[key]) if key in numeric else (row.get(key) or "").strip()
                    for key in Zone.__dataclass_fields__}
            zone = Zone(**args)
            if zone.zone.casefold() in names:
                raise ValueError("Duplicate zone name; use a distinct label for each observation.")
            names.add(zone.zone.casefold())
            zones.append(zone)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"CSV row {number}: {exc}") from exc
    if not zones:
        raise ValueError("CSV contains no observations.")
    if len(zones) > 200:
        raise ValueError("Maximum 200 observations per CSV.")
    return zones


def parse_filename(filename, reference_c=22.5, reference_basis="indoor_air"):
    match = re.fullmatch(r"(.+?)\(([-+\d.eE]+)\s+([-+\d.eE]+)\s+([-+\d.eE]+)\s+(\d+)\)\.(?:png|jpe?g)", filename, re.I)
    if not match:
        raise ValueError("Use Zone(average maximum minimum materialID).jpg or .png.")
    name, avg, high, low, material_id = match.groups()
    if int(material_id) not in MATERIALS:
        raise ValueError("Supported legacy material IDs are 1, 2 and 3; use CSV for other materials.")
    material, u_value = MATERIALS[int(material_id)]
    return Zone(name.strip(), float(avg), float(high), float(low), material,
                u_value, 1.0, reference_c, reference_basis,
                "Temperature transcribed in filename; area defaults to 1 m².")


def export_csv(rows):
    """Escape spreadsheet formula prefixes in user-provided text on export."""
    if not rows:
        return b""
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=list(rows[0]))
    writer.writeheader()
    for row in rows:
        safe = {key: "'" + val if isinstance(val, str) and val.lstrip().startswith(("=", "+", "-", "@")) else val
                for key, val in row.items()}
        writer.writerow(safe)
    return out.getvalue().encode("utf-8-sig")
