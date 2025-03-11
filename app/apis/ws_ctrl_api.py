# 导入系统库
import asyncio
import json
import threading

# 导入第三方库
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException, Depends
from loguru import logger
from sqlalchemy.orm import Session

# 导入自定义库
from app.extensions import get_ws_manager, get_rdbms, WebSocketManager
from app.cores.serial_ctrl import message_queue, SerialController

# 定义全局变量
router = APIRouter()

# 定义websocket端点
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, ws_manager: WebSocketManager = Depends(get_ws_manager), db: Session = Depends(get_rdbms)):
    try:
        logger.info(f"websocket connected: {websocket}")
        # 建立连接
        await ws_manager.connect(websocket)

        # 创建异步任务：接受串口数据并推送给前端 TODO:将该异步任务放置线程中去执行
        asyncio.create_task(send_serial_data(websocket))

        # 处理客户端请求
        await handle_client_request(websocket, db)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}, websocket: {websocket}")
    finally:
        await ws_manager.disconnect()


# 定义task： 接受串口数据并推送给前端
async def send_serial_data(websocket: WebSocket):
    try:
        while True:
            if not message_queue.empty():
                # 打印队列长度
                logger.info(f"queue length: {message_queue.qsize()}")
                # 获取数据 TODO:message中的图片数据要转换为base64数据格式
                message = message_queue.get()
                # 推送给前端
                await websocket.send_json(message)
                logger.info(f"send serial data to front: {message}")
                # 等待0.1秒
            # await asyncio.sleep(0.1)
    except WebSocketDisconnect as e:
        logger.info("websocket has disconnected!")
        return
    except WebSocketException as e:
        logger.info("websocket exception")
        return
    except RuntimeError as e:
        logger.error(f"run time error: {str(e)}")
        return

# 定义task：处理前端请求
async def handle_client_request(websocket: WebSocket, db: Session):
    try:
        # 创建串口控制器
        serial_ctrl = SerialController(db)
        message = ""

        while True:
            # 前端请求格式
            '''
            {
                "cmd": "set serial param",
                "param": {
                    "port": "COM1",
                    "baudrate": 115200,
                    ...
                }
            }
            '''
            cmd = await websocket.receive_json()
            logger.info(f"front request: {cmd}")

            # 处理前端start请求
            if cmd["cmd"] == "start":
                serial_ctrl.set_serial_param(cmd["param"])
                if not serial_ctrl.open_connection():
                    message = {
                        "type": "error",
                        "data": "serial connect failed"
                    }
                    logger.warning(message)
                    await websocket.send_json(message)
                    continue
                
                recv_thread = threading.Thread(target=serial_ctrl.recv_and_save_data, daemon=True)
                recv_thread.start()
                message = {
                    "type": "notification",
                    "data": "serial connect successfully"
                }
                logger.info(message)
                await websocket.send_json(message)
                
            # 处理前端stop请求
            elif cmd["cmd"] == "stop":
                serial_ctrl.close_connection()
                message = {
                    "type": "notification",
                    "data": "serial close successfully"
                }
                logger.info(message)
                await websocket.send_json(message)
            # 处理心跳
            elif cmd["cmd"] == "heart":
                logger.info(cmd)
                message = {
                    "type": "heart",
                    "data": "pong"
                }
                await websocket.send_json(message)
            # 异常处理
            else:
                message = {
                    "type": "error",
                    "data": "unknown command"
                }
                logger.warning(message)
                await websocket.send_json(message)
    except WebSocketDisconnect as e:
        logger.info("websocket has disconnected!")
        serial_ctrl.close_connection()
        return
    except WebSocketException as e:
        logger.info("websocket exception")
        serial_ctrl.close_connection()
        return
    except RuntimeError as e:
        serial_ctrl.close_connection()
        logger.error(f"run time error: {str(e)}")
        return