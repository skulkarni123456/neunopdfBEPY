from fastapi import APIRouter, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import tempfile, os, uuid, zipfile
from app.utils.files import save_upload_to_file, cleanup_paths
from pdf2image import convert_from_path
from PIL import Image

router = APIRouter()

def make_zip(files, dest_zip):
    with zipfile.ZipFile(dest_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for fpath, arcname in files:
            z.write(fpath, arcname)

@router.post("/pdf-to-jpg")
async def pdf_to_jpg(pdf: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    tmpdir = tempfile.mkdtemp(prefix="pdf2jpg_")
    try:
        inpath = await save_upload_to_file(pdf, tmpdir)
        images = convert_from_path(inpath, output_folder=tmpdir)
        outputs = []
        for i, img in enumerate(images):
            fname = os.path.join(tmpdir, f"page_{i+1}.jpg")
            img.save(fname, "JPEG")
            outputs.append((fname, os.path.basename(fname)))
        if len(outputs) == 1:
            background_tasks.add_task(cleanup_paths, [tmpdir])
            return FileResponse(outputs[0][0], filename=outputs[0][1], media_type="image/jpeg")
        zip_path = os.path.join(tmpdir, "pages_images.zip")
        make_zip(outputs, zip_path)
        background_tasks.add_task(cleanup_paths, [tmpdir])
        return FileResponse(zip_path, filename="pages_images.zip", media_type="application/zip")
    except Exception as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jpg-to-pdf")
async def jpg_to_pdf(images: list[UploadFile] = File(...), background_tasks: BackgroundTasks = None):
    tmpdir = tempfile.mkdtemp(prefix="jpg2pdf_")
    try:
        saved = []
        for f in images:
            p = await save_upload_to_file(f, tmpdir)
            saved.append(p)
        pil_imgs = [Image.open(p).convert("RGB") for p in saved]
        outpath = os.path.join(tmpdir, f"output_{uuid.uuid4().hex}.pdf")
        pil_imgs[0].save(outpath, save_all=True, append_images=pil_imgs[1:])
        background_tasks.add_task(cleanup_paths, [tmpdir])
        return FileResponse(outpath, filename="output.pdf", media_type="application/pdf")
    except Exception as e:
        cleanup_paths([tmpdir])
        raise HTTPException(status_code=500, detail=str(e))
