"""Build a clean, history-free upload package from an explicit source allowlist."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ["README.md", "CREDITS.md", "requirements.txt", "app.py", ".gitignore"]
PATTERNS = ["thermal_analysis/*.py", "data/*.csv", "docs/*.md", "tests/*.py",
            "scripts/*.py", ".github/workflows/*.yml"]


def public_files():
    paths = [ROOT / name for name in FILES]
    for pattern in PATTERNS:
        paths.extend(ROOT.glob(pattern))
    for path in paths:
        if not path.is_file() or not path.resolve().is_relative_to(ROOT):
            raise ValueError(f"Invalid public source: {path}")
    return sorted(set(paths))


def main():
    target = ROOT / "dist/galbraith-thermal-analysis.zip"
    target.parent.mkdir(exist_ok=True)
    paths = public_files()
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("ZIP verification failed")
    print(f"Created {target} ({len(paths)} public files)")


if __name__ == "__main__":
    main()
