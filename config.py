import json
import os

# 默认配置
DEFAULT_CONFIG = {
    "server": {
        "host": "localhost",
        "port": 8000,
        "reload": False  # exe模式下不支持reload=True
    },
    "storage": {
        "data_file": "data_storage.json"
    },
    "api": {
        "title": "JSON数据服务器",
        "description": "一个简单的JSON数据存储和查询服务"
    }
}

CONFIG_FILE = "config.json"

def load_config():
    """加载配置文件，如果配置文件不存在则创建默认配置"""
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 确保所有必要的配置都存在
        updated = False
        for section, values in DEFAULT_CONFIG.items():
            if section not in config:
                config[section] = values
                updated = True
            else:
                for key, value in values.items():
                    if key not in config[section]:
                        config[section][key] = value
                        updated = True
        
        if updated:
            # 保存更新后的配置
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        return config
    except Exception as e:
        print(f"加载配置文件出错: {str(e)}，使用默认配置")
        return DEFAULT_CONFIG 