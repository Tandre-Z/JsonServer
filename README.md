# JsonServer

一个简单的JSON数据存储和查询服务

## 使用

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 运行

```bash
python main.py
```

3. api文档

```bash
http://localhost:8080/docs
```

4. 打包

```bash
python build.py
```

5. 运行打包后的文件

```bash
dist/JsonServer.exe
```

6. 打包后的文件结构

```bash
dist/
    JsonServer.exe // 服务器主程序
    config.json // 配置文件
    server_debug.log // 日志文件
    data_storage.json // 数据存储文件
```
