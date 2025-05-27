import json

def main1():
    json_string = """
    [
        {
            "uuid": "3",
            "req": "GET /archive/CZ/KS3/123204004672858633/2022-07/19/1.2.345.6.789.3.1.2.64219988.13204.1658187395.2-1.3.12.2.1107.5.1.4.75831.30000022071512241475700155529/245-1.3.12.2.1107.5.1.4.75831.30000022071512241475700155774.dcm?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240821T053617Z&X-Amz-SignedHeaders=host&X-Amz-Expires=6000&X-Amz-Credential=AKLTgV1HoqgGTw-L4iMPyBEOOA%2F20240821%2FCN-SHANGHAI-2%2Fs3%2Faws4_request&X-Amz-Signature=5c0a4681af7d9e333f07e26318bc7b8f7f5b730f73875ba1b3e120b2756b0efb HTTP/1.1\\nHost: 20.16.10.114:8082\\nAccept-Encoding: identity\\nUser-Agent: python-urllib3/2.2.2",
            "rsp": "HTTP/1.1 200 OK\\nServer: nginx/1.24.0\\nDate: Wed, 21 Aug 2024 05:45:56 GMT\\nContent-Type: application/octet-stream\\nContent-Length: 285746\\nConnection: keep-alive\\nX-Application-Context: application\\nx-kss-request-id: f4f266b513b046179b185fe1d071049d\\nETag: \\"7f0fb930bcdc4d9245c93fcceeeee784\\"\\nContent-MD5: fw+5MLzcTZJFyT/M7u7nhA==\\nLast-Modified: Wed, 20 Jul 2022 02:40:03 GMT\\nx-amz-request-id: f4f266b513b046179b185fe1d071049d\\nAccept-Ranges: bytes",
            "reason": "Request successful (200 OK)",
            "label": "SUCCESS"
        }
    ]
    """

    try:
        # 反序列化JSON字符串
        data_list = json.loads(json_string)

        # 现在 data_list 是一个 Python 列表，其中每个元素都是一个字典
        print(f"反序列化成功！结果类型: {type(data_list)}")
        print(f"记录数量: {len(data_list)}")

        # 遍历列表并访问每个字典（记录）
        for record_index, record in enumerate(data_list):
            print(f"\n--- 记录 {record_index + 1} (类型: {type(record)}) ---")
            # 使用 .get('key') 更安全，如果键可能不存在，它会返回 None 而不是引发 KeyError
            print(f"  UUID: {record.get('uuid')}")
            print(f"  Reason: {record.get('reason')}")
            print(f"  Label: {record.get('label')}")

            # req 和 rsp 字段可能很长，可以选择性打印
            # print(f"  Req: {record.get('req')[:100]}...") # 打印前100个字符
            # print(f"  Rsp: {record.get('rsp')[:100]}...")

        # 访问特定记录及其字段
        if data_list:
            first_record = data_list[0]
            print(f"\n--- 第一个记录的详细信息 ---")
            print(f"  UUID: {first_record['uuid']}")
            print(f"  Req (原始，包含 \\n): {first_record['req'][:70]}...") # 显示部分原始req字符串

            # 如果你想在打印时看到实际的换行符而不是 '\\n'
            # 你可以替换它们。注意：在Python字符串中，'\\' 是一个转义字符，
            # 所以你需要用 '\\\\n' 来匹配字面上的 '\n' 字符串。


    except json.JSONDecodeError as e:
        print(f"JSON反序列化错误: {e}")
        print(f"错误发生在字符位置: {e.pos}")
        print(f"附近的文本: '{e.doc[max(0, e.pos-20):e.pos+20]}'")

def main2():
    import json

    # 这是你提供的原始字符串，它包含了 Markdown 代码块的语法
    markdown_json_string = """
    ```json
    [
      {
        "uuid": "exchange_1",
        "label": "CLASSIFICATION_FOR_EXCHANGE_1",
        "reason": "REASONING_FOR_EXCHANGE_1_CLASSIFICATION"
      },
      {
        "uuid": "exchange_2",
        "label": "CLASSIFICATION_FOR_EXCHANGE_2",
        "reason": "REASONING_FOR_EXCHANGE_2_CLASSIFICATION"
      }
    ]
    ```
    """

    # 1. 移除开头的 ```json\n
    # 2. 移除结尾的 \n```
    # 3. 使用 strip() 移除可能存在的额外空白字符
    #    （如开始和结束的空行）
    json_content_string = markdown_json_string.replace('```json', '', 1).replace('```', '', 1).strip()

    # 检查去除后的字符串
    print("--- 提取出的纯 JSON 内容 ---")
    print(json_content_string)
    print("-" * 30)

    try:
        # 现在，这个字符串应该是一个有效的 JSON 数组字符串，可以被 json.loads() 处理
        data_list = json.loads(json_content_string)

        print(f"反序列化成功！结果类型: {type(data_list)}")
        print(f"列表中包含的元素数量: {len(data_list)}")

        # 打印第一个元素（一个字典）
        print("\n第一个元素:")
        print(data_list[0])

        # 访问特定字段
        print(f"\n第一个元素的 uuid: {data_list[0]['uuid']}")

    except json.JSONDecodeError as e:
        print(f"JSON 解码错误: {e}")
        print(f"错误发生在字符位置: {e.pos}")
        print(f"附近的文本: '{e.doc[max(0, e.pos - 20):e.pos + 20]}'")

def main3():
    import pandas as pd
    import os

    file_name = 'my_data.csv'

    # --- 第一次写入数据 (创建文件并写入列头) ---
    data_initial = {
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'score': [85, 90, 78]
    }
    df_initial = pd.DataFrame(data_initial)

    # 写入CSV，如果文件不存在则创建，如果存在则覆盖
    df_initial.to_csv(file_name, index=False, header=True)
    print("--- 第一次写入数据 ---")
    with open(file_name, 'r') as f:
        print(f.read())
    print("-" * 30)

    # --- 第二次追加数据 (不写入列头) ---
    data_append_1 = {
        'id': [4, 5],
        'name': ['David', 'Eve'],
        'score': [92, 88]
    }
    df_append_1 = pd.DataFrame(data_append_1)

    # 使用 mode='a' 追加数据，header=False 避免重复写入列头
    df_append_1.to_csv(file_name, mode='a', index=False, header=False)
    print("--- 第二次追加数据 ---")
    with open(file_name, 'r') as f:
        print(f.read())
    print("-" * 30)

    # --- 第三次追加数据 (再次追加，不写入列头) ---
    data_append_2 = {
        'id': [6],
        'name': ['Frank'],
        'score': [75]
    }
    df_append_2 = pd.DataFrame(data_append_2)

    df_append_2.to_csv(file_name, mode='a', index=False, header=False)
    print("--- 第三次追加数据 ---")
    with open(file_name, 'r') as f:
        print(f.read())
    print("-" * 30)

    # 清理文件
    # os.remove(file_name)


if __name__ == '__main__':
    main3()