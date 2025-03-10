import PyInstaller.__main__
import os

# 打包命令
PyInstaller.__main__.run([
    'main.py',                      # 入口文件
    '--name=JsonServer',            # 生成的exe名称
    '--onefile',                    # 单文件模式
    '--console',                    # 显示控制台
    '--add-data=config.json;.',     # 添加配置文件
    # '--icon=server.ico',            # 注释掉图标文件
    '--hidden-import=uvicorn.logging',
    '--hidden-import=uvicorn.lifespan',
    '--hidden-import=uvicorn.lifespan.on',
    '--hidden-import=uvicorn.lifespan.off',
    '--hidden-import=asyncio',
    '--hidden-import=email.mime.text',
    '--hidden-import=email.mime.application',
    '--hidden-import=email.mime.multipart',
])

print("打包完成！") 