"""
配置文件，存储所有可配置参数
"""
import os
import json
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# 加载.env文件中的环境变量（如果存在）
env_path = Path(__file__).parents[1] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# 用户配置目录
USER_CONFIG_DIR = os.path.expanduser("~/.ai-text-generator")
USER_CONFIG_FILE = os.path.join(USER_CONFIG_DIR, "config.json")

# 默认配置
DEFAULT_CONFIG = {
    # API配置
    "sglang_endpoint": "https://aip.sangfor.com.cn:12588/v1",
    "api_key": "sk-FRdCi5yEKxUyDcRp2fBd67921aCa4bA391506cE7C3Dd7863",

    # 模型配置
    "default_model": "qwen7b",
    "available_models": ["qwen7b", "deepseek-r1-distill-qwen7b", "secgpt7b", "qwen3-8b"],

    # 生成参数
    "temperature": 0.0,
    "max_tokens": 1024,
    "top_p": 1.0,
    "top_k": 20,
    "enable_thinking": False,
    "timeout": 120000,

    # 应用设置
    "history_size": 10,
    "log_level": "INFO",
    "api_server_host": "localhost",
    "api_server_port": 8000
}


# 导出所有配置为模块变量
# API配置
SGLANG_ENDPOINT = "http://localhost:11434/v1"
API_KEY = "fake-key"

# 模型配置
DEFAULT_MODEL = "qwen3:8b"
AVAILABLE_MODELS = ["qwen7b", "deepseek-r1-distill-qwen7b", "secgpt7b", "qwen3-8b"]

# 生成参数
DEFAULT_TEMPERATURE = float("0")
DEFAULT_MAX_TOKENS = int("4096")
DEFAULT_TOP_P = float("1.0")
DEFAULT_TOP_K = int("20")
DEFAULT_THINKING = False
DEFAULT_TIMEOUT = int("120000")