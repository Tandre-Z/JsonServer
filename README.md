# JsonServer

一个简单的JSON数据存储和查询服务

## 功能特点

- 支持自定义ID的数据存储
- 支持JSON格式的查询条件
- 完整的错误处理和验证
- 可配置的服务器设置
- 自动创建和更新配置文件

## 使用

1. 安装依赖

    ```bash
    pip install -r requirements_windows.txt
    ```

2. 运行

    ```bash
    python main.py
    ```

3. API文档

    ```bash
    http://localhost:8000/docs
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

## 配置说明

配置文件 `config.json` 包含以下设置：

```json
{
    "server": {
        "host": "localhost",
        "port": 8000,
        "reload": false
    },
    "storage": {
        "data_file": "data_storage.json"
    },
    "api": {
        "title": "JSON数据服务器",
        "description": "一个简单的JSON数据存储和查询服务"
    }
}
```

## 使用示例

1. 发送/添加数据(post)

    ```bash
    curl -X POST "http://localhost:8000/data" -H "Content-Type: application/json" -d '{"data": {"name": "测试", "value": 123}, "id": "custom_id"}'
    ```

2. 查询数据(get)

   - 获取所有数据

   ```bash
   curl -X GET "http://localhost:8000/data"
   ```

   - 获取指定数据

   ```bash
   curl -X GET "http://localhost:8000/data?id=custom_id"
   ```

   - 使用JSON查询条件

   ```bash
   curl -X GET "http://localhost:8000/data?query=%7B%22name%22%3A%22测试%22%7D"
   ```

3. 更新数据(put)

    ```bash
    curl -X PUT "http://localhost:8000/data/custom_id" -H "Content-Type: application/json" -d '{"data": {"name": "更新后的数据", "value": 456}}'
    ```

4. 删除数据(delete)

    ```bash
    curl -X DELETE "http://localhost:8000/data/custom_id"
    ```

## 错误处理

服务器会返回标准化的错误响应，包含以下字段：

- code: 错误代码
- message: 错误信息
- success: 操作是否成功
- details: 详细的错误信息（如果有）

示例错误响应：

```json
{
    "code": 404,
    "message": "未找到ID为custom_id的数据",
    "success": false
}
```
