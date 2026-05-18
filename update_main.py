with open("app/main.py", "r") as f:
    content = f.read()

# 1. Добавляем импорт database после последнего импорта
old_import = "from fastapi.staticfiles import StaticFiles"
new_import = "from fastapi.staticfiles import StaticFiles\nfrom app.database import init_db, save_analysis, get_history"
content = content.replace(old_import, new_import, 1)

# 2. Добавляем init_db() после создания app
old_app = 'app = FastAPI(title="Manhwa/Webtoon Analyzer")'
new_app = 'app = FastAPI(title="Manhwa/Webtoon Analyzer")\n\ninit_db()'
content = content.replace(old_app, new_app, 1)

# 3. Добавляем save_analysis перед return в /analyze
old_return = '    return {"panels_found": panels_found, "total_scenes": total_scenes, "recap": recap}'
new_return = '    save_analysis(title, characters, panels_found, total_scenes, recap)\n    return {"panels_found": panels_found, "total_scenes": total_scenes, "recap": recap}'
content = content.replace(old_return, new_return, 1)

# 4. Добавляем /history endpoint перед mount
old_mount = 'app.mount("/static"'
new_endpoint = '''@app.get("/history")
def get_analysis_history(limit: int = 10):
    """Return last N analyses from database"""
    return get_history(limit)


'''
content = content.replace(old_mount, new_endpoint + 'app.mount("/static"', 1)

with open("app/main.py", "w") as f:
    f.write(content)

print("Done!")
