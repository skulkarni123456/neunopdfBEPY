from fastapi import APIRouter, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import tempfile, os, shutil, zipfile, uuid
from app.utils.files import save_upload_to_file, cleanup_paths
from pypdf import PdfReader, PdfWriter
import subprocess

router = APIRouter()

def make_zip(files, dest_zip):
    with zipfile.ZipFile(dest_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for fpath, arcname in files:
            z.write(fpath, arcname)

@router.post("/merge")
async def merge(files: list[UploadFile] = File(...), background_tasks: BackgroundTasks = None):
    tmpdir = tempfile.mkdtemp(prefix="merge_")
    saved = []
    try:
        for f in files:
            p = await save_upload_to_file(f, tmpdir)
            saved.append(p)
        writer = PdfWriter()
        for p in saved:
            reader = PdfReader(p)
            for page in reader.pages:
                writer.add_page(page)
        out_path = os.path.join(tmpdir, f"merged_{uuid.uuid4().hex}.pdf")
        with open(out_path, "wb") as fh:
            writer.write(fh)
        # deliver single file
        background_tasks.add_task(cleanup_paths, [tmpdir])
        return FileResponse(out_path, filename="merged.pdf", media_type="application/pdf")
    except Exception as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/split")
async def split(pdf: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    tmpdir = tempfile.mkdtemp(prefix="split_")
    outputs = []
    try:
        inpath = await save_upload_to_file(pdf, tmpdir)
        reader = PdfReader(inpath)
        for i in range(len(reader.pages)):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            outp = os.path.join(tmpdir, f"page_{i+1}.pdf")
            with open(outp, "wb") as fh:
                writer.write(fh)
            outputs.append((outp, os.path.basename(outp)))
        # if multiple files -> zip
        if len(outputs) == 1:
            background_tasks.add_task(cleanup_paths, [tmpdir])
            return FileResponse(outputs[0][0], filename=outputs[0][1], media_type="application/pdf")
        zip_path = os.path.join(tmpdir, "split_pages.zip")
        make_zip(outputs, zip_path)
        background_tasks.add_task(cleanup_paths, [tmpdir])
        return FileResponse(zip_path, filename="split_pages.zip", media_type="application/zip")
    except Exception as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract")
async def extract(pdf: UploadFile = File(...), pages: str = "1", background_tasks: BackgroundTasks = None):
    # pages param example: "1-3,5,7"
    tmpdir = tempfile.mkdtemp(prefix="extract_")
    try:
        inpath = await save_upload_to_file(pdf, tmpdir)
        reader = PdfReader(inpath)
        idxs = []
        for part in pages.split(","):
            if "-" in part:
                a,b = part.split("-",1)
                idxs.extend(range(int(a)-1, int(b)))
            else:
                idxs.append(int(part)-1)
        outputs = []
        for idx in idxs:
            if idx < 0 or idx >= len(reader.pages):
                continue
            w = PdfWriter()
            w.add_page(reader.pages[idx])
            outp = os.path.join(tmpdir, f"page_{idx+1}.pdf")
            with open(outp, "wb") as fh:
                w.write(fh)
            outputs.append((outp, os.path.basename(outp)))
        if not outputs:
            cleanup_paths([tmpdir])
            raise HTTPException(status_code=400, detail="No valid pages")
        if len(outputs) == 1:
            background_tasks.add_task(cleanup_paths, [tmpdir])
            return FileResponse(outputs[0][0], filename=outputs[0][1], media_type="application/pdf")
        zip_path = os.path.join(tmpdir, "extracted_pages.zip")
        make_zip(outputs, zip_path)
        background_tasks.add_task(cleanup_paths, [tmpdir])
        return FileResponse(zip_path, filename="extracted_pages.zip", media_type="application/zip")
    except Exception as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compress")
async def compress(pdf: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    tmpdir = tempfile.mkdtemp(prefix="compress_")
    try:
        inpath = await save_upload_to_file(pdf, tmpdir)
        outpath = os.path.join(tmpdir, "compressed.pdf")
        # use ghostscript for compression
        cmd = [
            "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/ebook", "-dNOPAUSE", "-dQUIET", "-dBATCH",
            f"-sOutputFile={outpath}", inpath
        ]
        subprocess.run(cmd, check=True, timeout=120)
        background_tasks.add_task(cleanup_paths, [tmpdir])
        return FileResponse(outpath, filename="compressed.pdf", media_type="application/pdf")
    except subprocess.CalledProcessError as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail="Compression failed")
    except Exception as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail=str(e))
