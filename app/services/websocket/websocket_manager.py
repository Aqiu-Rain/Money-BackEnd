# 导入系统库
from loguru import logger

# 导入第三方库
from fastapi import WebSocket

# 导入自定义库

# 定义全局变量

# 定义websocket管理器
class WebSocketManager:
    def __init__(self):
        self.active_connection: WebSocket = None

    # 添加连接
    async def connect(self, websocket: WebSocket):
        if self.active_connection:
            await self.disconnect()
        await websocket.accept()
        self.active_connection = websocket
        logger.info(f"connect websocket sucessfully : {websocket}")

    # 移除连接
    async def disconnect(self):
        try:
            if self.active_connection:
                await self.active_connection.close()
                self.active_connection = None
                logger.info(f"disconnect websocket successfully: {self.active_connection}")
        except RuntimeError as e:
            logger.error(f"disconnect websocket failed: {str(e)}")

    # def send_data_to_client(self, data: json):
    #     if self.active_connection:
    #         await self.active_connection.send_json(data)