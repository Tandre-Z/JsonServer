from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union, Generic, TypeVar
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

# 定义通用响应模型
T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    code: int
    message: str
    success: bool
    data: Optional[T] = None

# 定义通用数据模型
class DataItem(BaseModel):
    data: Dict[str, Any]  # 存储任意JSON数据
    id: Optional[str] = None  # 可选的自定义ID
    
    class Config:
        arbitrary_types_allowed = True

# 数据存储函数
def save_data(data: DataItem) -> Dict:
    try:
        # 读取现有数据
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            stored_data = json.load(f)
        
        # 如果提供了自定义ID，检查是否已存在
        if data.id is not None:
            for item in stored_data:
                if item.get("id") == data.id:
                    raise DataOperationError(f"ID {data.id} 已存在", 400)
        
        # 创建新条目
        entry = {
            "id": data.id or str(len(stored_data) + 1),  # 使用自定义ID或生成新ID
            "timestamp": datetime.now().isoformat(),
            "data": data.data
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
def get_data(
    id: Optional[str] = None,
    query: Optional[Dict[str, Any]] = None
) -> List[Dict]:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            stored_data = json.load(f)
        
        # 如果提供了ID，直接查询
        if id is not None:
            result = [item for item in stored_data if item.get("id") == id]
            if not result:
                raise HTTPException(status_code=404, detail=f"未找到ID为{id}的数据")
            return result
        
        # 如果提供了查询条件，进行过滤
        if query is not None:
            result = stored_data
            for key, value in query.items():
                result = [item for item in result if item.get("data", {}).get(key) == value]
            return result
        
        # 返回所有数据
        return stored_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取数据时出错: {str(e)}")

# POST端点 - 添加数据
@app.post("/data", response_model=ResponseModel[Dict])
async def add_data(item: DataItem):
    """
    添加新的数据项
    """
    stored_item = save_data(item)
    return ResponseModel(
        code=200,
        message="数据已成功保存",
        success=True,
        data=stored_item
    )

# GET端点 - 查询数据
@app.get("/data", response_model=ResponseModel[List[Dict]])
async def query_data(
    id: Optional[str] = Query(None, description="按ID查询"),
    query: Optional[str] = Query(None, description="JSON格式的查询条件")
):
    """
    查询数据，支持按ID查询或使用JSON查询条件
    """
    query_dict = None
    if query:
        try:
            query_dict = json.loads(query)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="查询条件格式错误")
    
    data = get_data(id, query_dict)
    return ResponseModel(
        code=200,
        message="查询成功",
        success=True,
        data=data
    )

# PUT端点 - 更新数据
@app.put("/data/{item_id}", response_model=ResponseModel[Dict])
async def update_data(item_id: str, item: DataItem):
    """
    更新指定ID的数据
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            stored_data = json.load(f)
        
        # 查找指定ID的数据
        item_index = None
        for index, stored_item in enumerate(stored_data):
            if stored_item.get("id") == item_id:
                item_index = index
                break
        
        if item_index is None:
            raise DataOperationError(f"未找到ID为{item_id}的数据", 404)
        
        # 更新数据
        updated_item = {
            "id": item_id,
            "timestamp": datetime.now().isoformat(),
            "data": item.data
        }
        
        stored_data[item_index] = updated_item
        
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(stored_data, f, ensure_ascii=False, indent=2)
            
        return ResponseModel(
            code=200,
            message="数据已成功更新",
            success=True,
            data=updated_item
        )
    except Exception as e:
        raise DataOperationError(f"更新数据时出错: {str(e)}", 500)

# DELETE端点 - 删除数据
@app.delete("/data/{item_id}", response_model=ResponseModel[Dict])
async def delete_data(item_id: str):
    """
    删除指定ID的数据
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            stored_data = json.load(f)
        
        # 查找指定ID的数据
        item_index = None
        deleted_item = None
        for index, item in enumerate(stored_data):
            if item.get("id") == item_id:
                item_index = index
                deleted_item = item
                break
        
        if item_index is None:
            raise DataOperationError(f"未找到ID为{item_id}的数据", 404)
        
        stored_data.pop(item_index)
        
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(stored_data, f, ensure_ascii=False, indent=2)
            
        return ResponseModel(
            code=200,
            message="数据已成功删除",
            success=True,
            data=deleted_item
        )
    except Exception as e:
        raise DataOperationError(f"删除数据时出错: {str(e)}", 500)

# 错误处理增强部分
# 1. HTTP异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "success": False,
            "data": None
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
            "success": False,
            "data": None
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
            "success": False,
            "data": None
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
            "success": False,
            "data": None
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