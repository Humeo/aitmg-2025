import json
import os
import time
from tqdm import tqdm
import pandas as pd
from string import Template # 假设你已经定义了Template
# from your_llm_client import create_chat_response # 假设你已经定义了create_chat_response

# 模拟 self.df, self.batch_size, self.current_prompt, self.create_chat_response, etc.
class MockSelf:
    def __init__(self):
        self.df = pd.DataFrame({
            'uuid': [f'uuid_{i}' for i in range(10)],
            'label': ['SUCCESS' if i % 2 == 0 else 'FAILURE' for i in range(10)],
            'data': [f'data_{i}' for i in range(10)]
        })
        self.batch_size = 3
        self.current_prompt = "Process the following data: ${traffic_exchanges_list_json}"
        # 模拟 LLM 响应，可能包含错误
        self.llm_responses = [
            '[{"uuid": "uuid_0", "label": "SUCCESS"}, {"uuid": "uuid_1", "label": "FAILURE"}]',
            '[{"uuid": "uuid_2", "label": "SUCCESS"}, {"uuid": "uuid_3", "label": "SUCCESS"}]', # 模拟一个预测错误
            '[{"uuid": "uuid_4", "label": "FAILURE"}, {"uuid": "uuid_5", "label": "FAILURE"}]',
            '[{"uuid": "uuid_6", "label": "SUCCESS"}, {"uuid": "uuid_7", "label": "FAILURE"}]',
            '{"uuid": "uuid_8", "label": "SUCCESS"}', # 模拟非列表JSON
            'Invalid JSON Response' # 模拟完全无效的JSON
        ]
        self.response_idx = 0

    def create_chat_response(self, prompt):
        # print(f"LLM Prompt: {prompt[:100]}...") # 打印部分prompt
        response = self.llm_responses[self.response_idx]
        self.response_idx = (self.response_idx + 1) % len(self.llm_responses)
        return response

# 假设这是你的类方法
def process_and_save(self, save_file, unlabeled_data=False):
    num_rows = len(self.df)
    true_labels = []
    predictions = []
    review_output = {"label": "", "reason": ""} # 确保 review_output 在循环外初始化，或者每次循环开始时初始化

    print(f"Attempting to write to: {save_file + '.jsonl'}")
    print(f"Total rows to process: {num_rows}")
    print(f"Batch size: {self.batch_size}")

    with open(save_file + ".jsonl", 'w', encoding='utf-8') as f_out:
        for i in tqdm(range(0, num_rows, self.batch_size), ncols=80):
            start_idx = i
            end_idx = min(i + self.batch_size, num_rows)

            print(f"\n--- Processing batch {start_idx}-{end_idx} ---") # 打印批次信息

            batch_df = self.df.iloc[start_idx:end_idx]
            batch_json = batch_df.to_json(orient="records")
            template = Template(self.current_prompt)
            formatted_prompt = template.render(traffic_exchanges_list_json=batch_json)

            try:
                llm_output = self.create_chat_response(formatted_prompt)
                print(f"LLM Raw Output (first 200 chars): {llm_output[:200]}...") # 打印LLM原始输出

                json_content_string = llm_output.replace('```json', '', 1).replace('```', '', 1).strip()
                print(f"Cleaned JSON String (first 200 chars): {json_content_string[:200]}...") # 打印清理后的JSON字符串

                data_list = json.loads(json_content_string)
                print(f"Parsed data_list length: {len(data_list) if isinstance(data_list, list) else 'Not a list'}") # 打印解析后的列表长度

                if not isinstance(data_list, list):
                    print("Warning: LLM output parsed as non-list JSON. Skipping record writing for this batch.")
                    continue # 跳过当前批次，因为期望的是一个列表

                if unlabeled_data:
                    for record in data_list:
                        json.dump(record, f_out, ensure_ascii=False)
                        f_out.write('\n')
                else:
                    for record in data_list:
                        json.dump(record, f_out, ensure_ascii=False)
                        f_out.write('\n')

                        if "uuid" not in record:
                            print(f"Warning: Record missing 'uuid' key: {record}")
                            continue # 跳过没有uuid的记录

                        row = batch_df[batch_df['uuid'] == record["uuid"]]
                        if row.empty:
                            print(f"Warning: UUID {record['uuid']} from LLM not found in original batch_df.")
                            continue # 跳过找不到对应uuid的记录

                        true_label = row['label'].iloc[0] # 使用 .iloc[0] 更安全
                        # 确保 record["label"] 存在
                        prediction = "UNKNOWN"
                        if "label" in record:
                            if "SUCCESS" in record["label"]:
                                prediction = "SUCCESS"
                            elif "FAILURE" in record["label"]:
                                prediction = "FAILURE"
                        else:
                            print(f"Warning: LLM record missing 'label' key: {record}")


                        true_labels.append(true_label)
                        predictions.append(prediction)

                        if prediction != true_label:
                            mis_json = {
                                "uuid": record.get('uuid'),
                                "true_label": true_label,
                                "predicted_label": prediction,
                                "review_output": review_output, # review_output 此时是默认值
                                "llm_output": record
                            }
                            json.dump(mis_json, f_out, ensure_ascii=False)
                            f_out.write('\n')

                # review_output = {"label": "", "reason":""} # 这个应该在循环外初始化，或者根据需要更新

                time.sleep(0.5)

            except json.JSONDecodeError as e:
                print(f"JSONDecodeError in batch {start_idx}-{end_idx}: {e}")
                print(f"Problematic JSON string (first 500 chars): {json_content_string[:500]}...")
            except IndexError as e: # 捕获 row['label'][0] 这种可能出现的错误
                print(f"IndexError in batch {start_idx}-{end_idx}: {e}")
                print(f"Context: Likely an issue with finding UUID or accessing label for record: {record.get('uuid')}")
            except Exception as e:
                print(f"General Error processing batch {start_idx}-{end_idx}: {e}")
                import traceback
                traceback.print_exc()

# 运行示例
mock_instance = MockSelf()
process_and_save(mock_instance, "output_data", unlabeled_data=False)

