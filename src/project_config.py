from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Main project folders
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLES_DIR = DATA_DIR / "samples"

NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Create folders if they do not exist
for folder in [
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    SAMPLES_DIR,
    NOTEBOOKS_DIR,
    OUTPUTS_DIR,
    REPORTS_DIR,
]:
    folder.mkdir(parents=True, exist_ok=True)

print("Abuja LULC project paths loaded successfully.")
print(f"Project root: {PROJECT_ROOT}")
