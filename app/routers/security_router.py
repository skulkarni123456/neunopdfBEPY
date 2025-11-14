from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import tempfile, os, subprocess
from app.utils.files import save_upload_to_file, cleanup_paths

router = APIRouter()

@router.post("/protect")
async def protect(pdf: UploadFile = File(...), password: str = Form(...), background_tasks: BackgroundTasks = None):
    tmpdir = tempfile.mkdtemp(prefix="protect_")
    try:
        inpath = await save_upload_to_file(pdf, tmpdir)
        outpath = os.path.join(tmpdir, "protected.pdf")
        cmd = ["qpdf", "--encrypt", password, password, "128", "--", inpath, outpath]
        subprocess.run(cmd, check=True)
        background_tasks.add_task(cleanup_paths, [tmpdir])
        return FileResponse(outpath, filename="protected.pdf", media_type="application/pdf")
    except subprocess.CalledProcessError:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail="qpdf encrypt failed")
    except Exception as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/unlock")
async def unlock(pdf: UploadFile = File(...), password: str = Form(...), background_tasks: BackgroundTasks = None):
    tmpdir = tempfile.mkdtemp(prefix="unlock_")
    try:
        inpath = await save_upload_to_file(pdf, tmpdir)
        outpath = os.path.join(tmpdir, "unlocked.pdf")
        cmd = ["qpdf", f"--password={password}", "--decrypt", inpath, outpath]
        subprocess.run(cmd, check=True)
        background_tasks.add_task(cleanup_paths, [tmpdir])
        return FileResponse(outpath, filename="unlocked.pdf", media_type="application/pdf")
    except subprocess.CalledProcessError:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail="qpdf decrypt failed")
    except Exception as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail=str(e))
