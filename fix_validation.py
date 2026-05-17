f = open('app/main.py', 'r')
content = f.read()
f.close()

content = content.replace(
    'from fastapi import FastAPI, UploadFile, File',
    'from fastapi import FastAPI, UploadFile, File, HTTPException'
)

old = '    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:\n        tmp.write(await file.read())\n        tmp_path = tmp.name'
new = '    if file.content_type not in ["image/jpeg", "image/png"]:\n        raise HTTPException(status_code=400, detail="Only JPG/PNG files allowed")\n    data = await file.read()\n    if len(data) > 5 * 1024 * 1024:\n        raise HTTPException(status_code=400, detail="File too large. Max 5MB")\n    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:\n        tmp.write(data)\n        tmp_path = tmp.name'

if old in content:
    content = content.replace(old, new)
    print("Done!")
else:
    print("Pattern not found")

f = open('app/main.py', 'w')
f.write(content)
f.close()
