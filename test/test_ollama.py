from openai import OpenAI
import json

# 创建客户端连接到本地Ollama服务
client = OpenAI(
    base_url="http://localhost:11434/v1",  # 注意使用v1路径以兼容OpenAI格式
    api_key="fake-key"  # 可以是任意字符串，除非你配置了API密钥
)

# 发送聊天请求
response = client.chat.completions.create(
    model="qwen3:8b",  # 使用已下载的模型名称
    messages=[
        {"role": "user", "content": "hello"},

    ],
    extra_body = {"chat_template_kwargs": {"enable_thinking": False}},
    temperature=0.7
)


response2 = client.chat.completions.create(
    model="qwen3:8b",
    messages=[
        {"role": "system", "content": "你是一个安全分析专家。"},
        {"role": "user", "content": "分析这个请求: data=echo \"<?php eval($_REQUEST[1]);?>\" > 1.php"}
    ],
    tools=[{
        "type": "function",
        "function": {
            "name": "security_analysis",
            "description": "分析请求的安全隐患",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "分析原因"
                    },
                    "label": {
                        "type": "string",
                        "enum": ["SUCCESS", "FAILURE", "UNKNOWN"],
                        "description": "分析结果标签"
                    }
                },
                "required": ["reason", "label"]
            }
        }
    }],
    tool_choice={"type": "function", "function": {"name": "security_analysis"}}
)

# 获取结构化输出
tool_call = response2.choices[0].message.tool_calls[0]
function_args = json.loads(tool_call.function.arguments)

print(function_args)


print(response.choices[0].message.content)