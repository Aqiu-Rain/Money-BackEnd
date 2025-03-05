# 导入系统库
import os
import uvicorn

# 导入第三方库
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# 导入自定义库
from app import create_app
from app.settings import STATIC_DIR


# 定义全局变量
app = create_app()
app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, 'assets')), name="assets")

@app.get('/', response_class=HTMLResponse)
def index():
    with open(os.path.join(STATIC_DIR, 'index.html'), encoding='utf-8') as f:
        return f.read()


# 启动服务
if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=False)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
