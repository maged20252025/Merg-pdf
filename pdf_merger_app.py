
import streamlit as st
from PyPDF2 import PdfMerger
import os
import zipfile
import io
from pathlib import Path

st.set_page_config(page_title="دمج كل 5 ملفات PDF", layout="centered")
st.title("📚 دمج كل 5 ملفات PDF في ملف واحد")

uploaded_files = st.file_uploader("قم برفع ملفات PDF (يمكن رفع عدة ملفات)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    num_files = len(uploaded_files)
    st.success(f"تم رفع {num_files} ملف PDF")

    if st.button("🔄 بدء الدمج كل 5 ملفات"):
        # تقسيم كل 5 ملفات في مجموعة
        group_size = 5
        pdf_groups = [uploaded_files[i:i+group_size] for i in range(0, num_files, group_size)]

        output_files = []
        output_dir = Path("output_pdfs")
        output_dir.mkdir(exist_ok=True)

        for idx, group in enumerate(pdf_groups, start=1):
            merger = PdfMerger()
            for pdf in group:
                merger.append(pdf)
            merged_filename = output_dir / f"group_{idx}.pdf"
            with open(merged_filename, "wb") as f_out:
                merger.write(f_out)
            merger.close()
            output_files.append(merged_filename)

        # ضغط الملفات المدمجة في ملف ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for file_path in output_files:
                zipf.write(file_path, arcname=file_path.name)

        st.success("✅ تم الدمج بنجاح")

        # تقديم الملف المضغوط للتحميل
        st.download_button(
            label="📦 تحميل الملفات المدمجة بصيغة ZIP",
            data=zip_buffer.getvalue(),
            file_name="دمج_PDF.zip",
            mime="application/zip"
        )

        # تنظيف الملفات المؤقتة
        for file_path in output_files:
            os.remove(file_path)
