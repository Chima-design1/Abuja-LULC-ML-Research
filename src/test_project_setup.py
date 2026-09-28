from pathlib import Path

from project_config import (
    PROJECT_ROOT,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    SAMPLES_DIR,
    NOTEBOOKS_DIR,
    OUTPUTS_DIR,
    REPORTS_DIR,
)

folders = {
    "Project root": PROJECT_ROOT,
    "Raw data": RAW_DATA_DIR,
    "Processed data": PROCESSED_DATA_DIR,
    "Samples": SAMPLES_DIR,
    "Notebooks": NOTEBOOKS_DIR,
    "Outputs": OUTPUTS_DIR,
    "Reports": REPORTS_DIR,
}

print("Checking Abuja LULC project folders...")
print()

for name, folder in folders.items():
    status = "OK" if folder.exists() else "MISSING"
    print(f"{status:8} {name}: {folder}")

print()
print("Project folder check completed.")
