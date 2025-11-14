# NeunoPDF - FastAPI backend

Endpoints:
- POST /pdf/merge
- POST /pdf/split
- POST /pdf/extract (pages param)
- POST /pdf/compress
- POST /convert/word-to-pdf
- POST /convert/excel-to-pdf
- POST /convert/ppt-to-pdf
- POST /convert/pdf-to-word
- POST /convert/pdf-to-excel
- POST /convert/pdf-to-ppt
- POST /convert/pdf-to-jpg
- POST /convert/jpg-to-pdf
- POST /security/protect
- POST /security/unlock

Notes:
- Requires system binaries: libreoffice (soffice), ghostscript (gs), poppler-utils, qpdf.
- Always returns a ZIP when multiple files result.
- No Swagger UI (docs disabled).
- Temporary files are deleted immediately after response (background cleanup).
