from openai import OpenAI

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

print(response.choices[0].message.content)