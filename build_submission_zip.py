import zipfile
import os

zip_name = "ABPS_Project_Submission_Krish_Desai.zip"
base_dir = r"c:\Users\Hp\OneDrive\Desktop\railway system"

# Files to place at the root of the ZIP
root_files = [
    "ABPS_Project_Presentation.pptx",
    "ABPS_Software_Requirements_Specification.pdf",
    "ABPS_Project_GitHub_Links.pdf",
]

# Items to place inside Source_Code/
source_items = [
    "backend",
    "frontend",
    "public",
    "abps.db",
    "app.js",
    "index.html",
    "modal_snippet.html",
    "package.json",
    "README.md",
    "requirements.txt",
    "start.bat",
    "stop.bat",
    ".gitignore",
    "generate_presentation_pptx.py",
    "generate_srs_pdf.py",
    "generate_github_links_pdf.py"
]

# Build new zip
zip_path = os.path.join(base_dir, zip_name)
if os.path.exists(zip_path):
    os.remove(zip_path)

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    # 1. Add root files
    for rf in root_files:
        full_p = os.path.join(base_dir, rf)
        if os.path.exists(full_p):
            zf.write(full_p, arcname=rf)
            print(f"Added to root: {rf}")
        else:
            print(f"WARNING: Root file missing: {rf}")

    # 2. Add Source_Code/ items
    for item in source_items:
        full_p = os.path.join(base_dir, item)
        if not os.path.exists(full_p):
            print(f"WARNING: Source item missing: {item}")
            continue
        if os.path.isdir(full_p):
            for root, dirs, files in os.walk(full_p):
                # Exclude __pycache__, .git, etc.
                dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', '.pytest_cache')]
                for f in files:
                    if f.endswith(('.pyc', '.pyo')):
                        continue
                    file_full = os.path.join(root, f)
                    rel = os.path.relpath(file_full, base_dir)
                    arcname = os.path.join("Source_Code", rel)
                    zf.write(file_full, arcname=arcname)
        else:
            arcname = os.path.join("Source_Code", item)
            zf.write(full_p, arcname=arcname)
            print(f"Added to Source_Code/: {item}")

size_mb = os.path.getsize(zip_path) / (1024 * 1024)
print(f"\nFinal ZIP created successfully: {zip_path}")
print(f"Total Size: {size_mb:.2f} MB (Portal limit: 255 MB)")

# Verify contents
print("\n--- ZIP Contents Top Level ---")
with zipfile.ZipFile(zip_path, 'r') as zf:
    namelist = zf.namelist()
    top_entries = sorted(list(set([n.split('/')[0] for n in namelist])))
    for entry in top_entries:
        print(" -", entry)
    print(f"\nTotal files in zip: {len(namelist)}")
