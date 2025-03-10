import os
import sys
import uvicorn
import traceback
import logging
from server import app
from config import load_config

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("json_server")

def resource_path(relative_path):
    """获取资源的绝对路径，在打包后仍能正常工作"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def main():
    try:
        # 加载配置
        logger.info("正在加载配置...")
        config = load_config()
        
        # 打印欢迎信息
        print("=" * 50)
        print(f"JSON数据服务器已启动")
        print("=" * 50)
        print(f"服务器地址: http://{config['server']['host']}:{config['server']['port']}")
        print(f"API文档: http://{config['server']['host']}:{config['server']['port']}/docs")
        print(f"数据文件: {config['storage']['data_file']}")
        print("=" * 50)
        print("按Ctrl+C停止服务器")
        
        # 启动服务器 - 修改以解决DLL问题
        logger.info("正在启动服务器...")
        uvicorn.run(
            app, 
            host=config["server"]["host"], 
            port=config["server"]["port"],
            log_level="info",
            loop="asyncio",       # 使用asyncio而不是uvloop
            # http="httptools",   # 注释掉这行
            ws="none"             # 禁用WebSockets
        )
    except Exception as e:
        error_msg = f"服务器启动失败: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        with open("error.log", "w") as f:
            f.write(f"{error_msg}\n\n")
            f.write(traceback.format_exc())
        print(f"错误: {error_msg}")
        print(f"详细信息已写入error.log文件")
        input("按任意键退出...")

if __name__ == "__main__":
    main() 