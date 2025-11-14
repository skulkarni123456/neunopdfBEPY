import os, aiofiles, shutil, glob, time

async def save_upload_to_file(upload_file, dst_dir):
    filename = upload_file.filename
    dest_path = os.path.join(dst_dir, filename)
    # ensure unique
    base, ext = os.path.splitext(dest_path)
    i = 0
    while os.path.exists(dest_path):
        i += 1
        dest_path = f"{base}_{i}{ext}"
    async with aiofiles.open(dest_path, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    return dest_path

def cleanup_paths(paths):
    # Immediately delete files/dirs (best-effort, silent)
    for p in paths:
        try:
            if os.path.isfile(p):
                os.remove(p)
            elif os.path.isdir(p):
                shutil.rmtree(p)
        except Exception:
            pass
