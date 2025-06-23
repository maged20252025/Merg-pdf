
import streamlit as st
from PyPDF2 import PdfMerger
import os
import zipfile
import io
from pathlib import Path

st.set_page_config(page_title="دمج كل 5 ملفات PDF", layout="centered")
st.title("📚 دمج كل 5 ملفات PDF في ملف واحد")

option = st.radio("اختر طريقة الرفع:", ("رفع ملفات PDF مباشرة", "رفع ملف ZIP يحتوي على PDF"))

uploaded_files = []
if option == "رفع ملفات PDF مباشرة":
    uploaded_files = st.file_uploader("قم برفع ملفات PDF", type="pdf", accept_multiple_files=True)
elif option == "رفع ملف ZIP يحتوي على PDF":
    zip_file = st.file_uploader("قم برفع ملف ZIP", type="zip")
    if zip_file:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            pdf_filenames = [name for name in zip_ref.namelist() if name.lower().endswith(".pdf")]
            if not pdf_filenames:
                st.error("📭 الملف المضغوط لا يحتوي على ملفات PDF")
            else:
                for name in pdf_filenames:
                    with zip_ref.open(name) as f:
                        uploaded_files.append(io.BytesIO(f.read()))
                st.success(f"تم استخراج {len(uploaded_files)} ملف PDF من الملف المضغوط")

if uploaded_files:
    num_files = len(uploaded_files)
    st.info(f"📄 عدد الملفات الجاهزة للدمج: {num_files}")

    if st.button("🔄 بدء الدمج كل 5 ملفات"):
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
