from fastapi import APIRouter, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import tempfile, os, shutil, uuid, subprocess
from app.utils.files import save_upload_to_file, cleanup_paths

router = APIRouter()

def soffice_convert(input_path, outdir):
    # soffice auto adds extension; call without extension on some installs; we'll call on full path
    cmd = ["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, input_path]
    subprocess.run(cmd, check=True, timeout=120)

@router.post("/word-to-pdf")
async def word_to_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    tmpdir = tempfile.mkdtemp(prefix="word2pdf_")
    try:
        inpath = await save_upload_to_file(file, tmpdir)
        # libreoffice expects a real file with extension
        soffice_convert(inpath, tmpdir)
        # result is same name but .pdf
        base = os.path.splitext(os.path.basename(inpath))[0]
        outpath = os.path.join(tmpdir, base + ".pdf")
        if not os.path.exists(outpath):
            raise HTTPException(status_code=500, detail="Conversion failed: output not found")
        background_tasks.add_task(cleanup_paths, [tmpdir])
        return FileResponse(outpath, filename=f"{base}.pdf", media_type="application/pdf")
    except subprocess.CalledProcessError:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail="LibreOffice conversion failed")
    except FileNotFoundError:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail="soffice not found on server")
    except Exception as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/excel-to-pdf")
async def excel_to_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    # same as above
    return await word_to_pdf(file, background_tasks)

@router.post("/ppt-to-pdf")
async def ppt_to_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    return await word_to_pdf(file, background_tasks)

@router.post("/pdf-to-word")
async def pdf_to_word(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    tmpdir = tempfile.mkdtemp(prefix="pdf2word_")
    try:
        inpath = await save_upload_to_file(file, tmpdir)
        # convert to docx using soffice
        cmd = ["soffice", "--headless", "--convert-to", "docx", "--outdir", tmpdir, inpath]
        subprocess.run(cmd, check=True, timeout=120)
        # find docx
        outfiles = [p for p in os.listdir(tmpdir) if p.lower().endswith(".docx")]
        if not outfiles:
            raise HTTPException(status_code=500, detail="Conversion failed")
        outpath = os.path.join(tmpdir, outfiles[0])
        background_tasks.add_task(cleanup_paths, [tmpdir])
        return FileResponse(outpath, filename=outfiles[0], media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    except Exception as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pdf-to-excel")
async def pdf_to_excel(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    tmpdir = tempfile.mkdtemp(prefix="pdf2excel_")
    try:
        inpath = await save_upload_to_file(file, tmpdir)
        cmd = ["soffice", "--headless", "--convert-to", "xlsx", "--outdir", tmpdir, inpath]
        subprocess.run(cmd, check=True, timeout=120)
        outfiles = [p for p in os.listdir(tmpdir) if p.lower().endswith(".xlsx")]
        if not outfiles:
            raise HTTPException(status_code=500, detail="Conversion failed")
        outpath = os.path.join(tmpdir, outfiles[0])
        background_tasks.add_task(cleanup_paths, [tmpdir])
        return FileResponse(outpath, filename=outfiles[0], media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pdf-to-ppt")
async def pdf_to_ppt(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    tmpdir = tempfile.mkdtemp(prefix="pdf2ppt_")
    try:
        inpath = await save_upload_to_file(file, tmpdir)
        cmd = ["soffice", "--headless", "--convert-to", "pptx", "--outdir", tmpdir, inpath]
        subprocess.run(cmd, check=True, timeout=120)
        outfiles = [p for p in os.listdir(tmpdir) if p.lower().endswith(".pptx")]
        if not outfiles:
            raise HTTPException(status_code=500, detail="Conversion failed")
        outpath = os.path.join(tmpdir, outfiles[0])
        background_tasks.add_task(cleanup_paths, [tmpdir])
        return FileResponse(outpath, filename=outfiles[0], media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
    except Exception as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail=str(e))
