from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union
import json
import os
from datetime import datetime
import uvicorn
import config

# 加载配置
CONFIG = config.load_config()

# 创建FastAPI应用
app = FastAPI(
    title=CONFIG["api"]["title"],
    description=CONFIG["api"]["description"]
)

# 定义数据存储路径
DATA_FILE = CONFIG["storage"]["data_file"]

# 确保数据文件存在
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)

# 定义数据模型
class DataItem(BaseModel):
    # 这里可以根据需要定义你的数据结构
    # 使用Any允许任何JSON结构
    data: Any
    
    class Config:
        arbitrary_types_allowed = True

# 数据存储函数
def save_data(data: Any) -> Dict:
    try:
        # 读取现有数据
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            stored_data = json.load(f)
        
        # 添加时间戳和ID
        entry = {
            "id": len(stored_data) + 1,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # 追加新数据
        stored_data.append(entry)
        
        # 写回文件
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(stored_data, f, ensure_ascii=False, indent=2)
            
        return entry
    except json.JSONDecodeError:
        raise DataOperationError("数据文件格式错误", 500)
    except PermissionError:
        raise DataOperationError("数据文件访问权限错误", 500)
    except IOError as e:
        raise DataOperationError(f"IO错误: {str(e)}", 500)
    except Exception as e:
        raise DataOperationError(f"存储数据时出错: {str(e)}", 500)

# 数据查询函数
def get_data(item_id: Optional[int] = None) -> List[Dict]:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            stored_data = json.load(f)
        
        if item_id is not None:
            # 查询特定ID的数据
            result = [item for item in stored_data if item["id"] == item_id]
            if not result:
                raise HTTPException(status_code=404, detail=f"未找到ID为{item_id}的数据")
            return result
        
        # 返回所有数据
        return stored_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取数据时出错: {str(e)}")

# POST端点 - 接收JSON数据
@app.post("/data", response_model=Dict)
async def receive_data(item: DataItem):
    """
    接收JSON数据并保存到本地存储
    """
    stored_item = save_data(item.data)
    return {"message": "数据已成功保存", "item": stored_item}

# GET端点 - 查询数据
@app.get("/data", response_model=List[Dict])
async def query_data(id: Optional[int] = Query(None, description="按ID查询特定数据项")):
    """
    查询存储的数据，可选择按ID筛选
    """
    return get_data(id)

# 添加数据更新函数
def update_data(item_id: int, new_data: Any) -> Dict:
    try:
        # 读取现有数据
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            stored_data = json.load(f)
        
        # 查找指定ID的数据
        item_index = None
        for index, item in enumerate(stored_data):
            if item["id"] == item_id:
                item_index = index
                break
        
        if item_index is None:
            raise DataOperationError(f"未找到ID为{item_id}的数据", 404)
        
        # 更新数据，保留原始ID和添加新的时间戳
        updated_item = {
            "id": item_id,
            "timestamp": datetime.now().isoformat(),
            "data": new_data
        }
        
        # 替换数据
        stored_data[item_index] = updated_item
        
        # 写回文件
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(stored_data, f, ensure_ascii=False, indent=2)
            
        return updated_item
    except json.JSONDecodeError:
        raise DataOperationError("数据文件格式错误", 500)
    except PermissionError:
        raise DataOperationError("数据文件访问权限错误", 500)
    except IOError as e:
        raise DataOperationError(f"IO错误: {str(e)}", 500)
    except Exception as e:
        if isinstance(e, DataOperationError):
            raise
        raise DataOperationError(f"更新数据时出错: {str(e)}", 500)

# PUT端点 - 更新JSON数据
@app.put("/data/{item_id}", response_model=Dict)
async def update_item(item_id: int, item: DataItem):
    """
    更新指定ID的JSON数据
    """
    updated_item = update_data(item_id, item.data)
    return {"message": "数据已成功更新", "item": updated_item}

# 获取最新数据函数
def get_latest_data(limit: Optional[int] = None) -> List[Dict]:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            stored_data = json.load(f)
        
        if not stored_data:
            return []
        
        # 按时间戳排序，最新的在前面
        sorted_data = sorted(stored_data, key=lambda x: x["timestamp"], reverse=True)
        
        # 如果指定了limit，则返回指定数量的最新数据
        if limit is not None and limit > 0:
            return sorted_data[:limit]
        
        return sorted_data
    except json.JSONDecodeError:
        raise DataOperationError("数据文件格式错误", 500)
    except Exception as e:
        raise DataOperationError(f"获取最新数据时出错: {str(e)}", 500)

# GET端点 - 获取最新数据
@app.get("/data/latest", response_model=List[Dict])
async def get_latest(limit: Optional[int] = Query(1, description="返回的最新数据条数，默认为1")):
    """
    获取最新的数据，按时间戳排序
    """
    return get_latest_data(limit)

# 错误处理增强部分
# 1. HTTP异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "success": False
        },
    )

# 2. 请求验证错误处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = []
    for error in exc.errors():
        error_details.append({
            "location": error["loc"],
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "数据验证错误",
            "details": error_details,
            "success": False
        },
    )

# 3. 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": f"服务器内部错误: {str(exc)}",
            "success": False
        },
    )

# 4. 添加一个自定义错误类和处理器
class DataOperationError(Exception):
    def __init__(self, detail: str, code: int = 400):
        self.detail = detail
        self.code = code
        super().__init__(self.detail)

@app.exception_handler(DataOperationError)
async def data_operation_exception_handler(request: Request, exc: DataOperationError):
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "message": exc.detail,
            "success": False
        },
    )

# 启动服务器
if __name__ == "__main__":
    print(f"服务器启动在 http://{CONFIG['server']['host']}:{CONFIG['server']['port']}")
    print(f"API文档: http://{CONFIG['server']['host']}:{CONFIG['server']['port']}/docs")
    print(f"数据存储文件: {DATA_FILE}")
    uvicorn.run(
        "server:app", 
        host=CONFIG["server"]["host"], 
        port=CONFIG["server"]["port"], 
        reload=CONFIG["server"]["reload"]
    ) 