import streamlit as st
import os
import shutil
from pathlib import Path
from mimetypes import guess_type

# Constants
BASE_DIR = Path("user_drive")
CATEGORIES = {
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"],
    "Documents": [".txt", ".doc", ".docx", ".odt"],
    "PDFs": [".pdf"],
    "Spreadsheets": [".xls", ".xlsx", ".csv"],
    "Code": [".py", ".js", ".html", ".css", ".cpp", ".java"],
    "Others": []
}
BASE_DIR.mkdir(exist_ok=True)

# Page Config
st.set_page_config(page_title="Streamlit Cloud Drive", layout="wide")
st.markdown("<h1 style='text-align:center;'>☁️ Streamlit Cloud Drive</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar: Folder creation
with st.sidebar:
    st.header("📁 Folder Manager")
    new_folder = st.text_input("Enter new folder name:")
    if st.button("➕ Create Folder"):
        folder_path = BASE_DIR / new_folder
        if folder_path.exists():
            st.warning("❗ Folder already exists!")
        else:
            folder_path.mkdir()
            st.success(f"✅ Folder '{new_folder}' created!")

    if st.button("🧹 Reset All"):
        shutil.rmtree(BASE_DIR)
        BASE_DIR.mkdir()
        st.success("🗑️ All data cleared!")

# Upload Section
st.subheader("📤 Upload Files")

folders = ["root"] + sorted([f.name for f in BASE_DIR.iterdir() if f.is_dir()])
selected_folder = st.selectbox("📌 Upload to Folder:", folders)

uploaded_files = st.file_uploader("Select files to upload", accept_multiple_files=True)

if st.button("🚀 Upload"):
    if not uploaded_files:
        st.warning("No files selected!")
    else:
        dest = BASE_DIR if selected_folder == "root" else BASE_DIR / selected_folder
        for file in uploaded_files:
            with open(dest / file.name, "wb") as f:
                f.write(file.read())
        st.success(f"✅ Uploaded {len(uploaded_files)} file(s) to '{selected_folder}'")

# Utility Function: Categorize
def get_file_category(filename):
    ext = os.path.splitext(filename)[1].lower()
    for cat, ext_list in CATEGORIES.items():
        if ext in ext_list:
            return cat
    return "Others"

# Display Section
st.markdown("## 🗃️ Files by Folder & Type")

for folder in folders:
    st.markdown(f"### 📂 {folder}")
    folder_path = BASE_DIR if folder == "root" else BASE_DIR / folder
    files = list(folder_path.glob("*"))
    
    if not files:
        st.info("No files in this folder.")
        continue

    categorized_files = {cat: [] for cat in CATEGORIES.keys()}
    for file in files:
        if file.is_file():
            category = get_file_category(file.name)
            categorized_files[category].append(file)

    tabs = st.tabs(list(categorized_files.keys()))
    for i, cat in enumerate(categorized_files.keys()):
        with tabs[i]:
            if not categorized_files[cat]:
                st.info(f"No {cat.lower()} files.")
            else:
                for file in categorized_files[cat]:
                    with st.expander(file.name):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"📄 Type: {guess_type(file)[0] or 'Unknown'}")
                            with open(file, "rb") as f:
                                st.download_button("⬇️ Download", data=f.read(), file_name=file.name)
                        with col2:
                            if st.button("🗑️ Delete", key=str(file)):
                                os.remove(file)
                                st.warning(f"Deleted: {file.name}")
                                st.experimental_rerun()
