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

## 使用示例

1. 发送/添加数据(post)

    ```bash
    curl -X POST "http://localhost:8000/data" -H "Content-Type: application/json" -d '{"data": {"name": "测试", "value": 123}}'
    ```

2. 查询数据(get)

   - 获取所有数据

   ```bash
   curl -X GET "http://localhost:8000/data"
   ```

   - 获取指定数据

   ```bash
   curl -X GET "http://localhost:8000/data/1"
   ```

   - 获取最新数据

   ```bash
   curl -X GET "http://localhost:8000/data/latest"
   ```

   - 获取最新几条数据

   ```bash
   curl -X GET "http://localhost:8000/data/latest?limit=10"
   ```

3. 更新数据(put)

    ```bash
    curl -X PUT "http://localhost:8000/data/1" -H "Content-Type: application/json" -d '{"data": {"name": "更新后的数据", "value": 456}}'
    ```

4. 删除数据(delete)

    ```bash
    curl -X DELETE "http://localhost:8000/data/1"
    ```
