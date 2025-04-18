import PyInstaller.__main__
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(current_dir, 'main.py')

# 打包命令
PyInstaller.__main__.run([
    main_path,                      # 入口文件
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