import threading

import webview
import uvicorn

from main import app

# 启动服务
t = threading.Thread(target=uvicorn.run, args=(app,), kwargs={"host": "127.0.0.1", "port": 8000})
t.daemon = True
t.start()

# 在PyWebview应用程序中加载FastAPI应用程序的URL
webview.create_window('Money', 'http://127.0.0.1:8000', min_size=(1400, 800))
webview.start()