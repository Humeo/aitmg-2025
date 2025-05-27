import math
import re
from datetime import datetime
from email.policy import default

import requests
from sympy import false

import utils
import click
import pandas as pd
import json
import os
import time
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np
import sys
from jinja2 import Template
from tqdm import tqdm
from openai import OpenAI
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config.setting as cfg
except ImportError:
    print("无法导入项目模块，请确保您在项目根目录下运行此脚本")
    sys.exit(1)


class PromptOptimizer:
    def __init__(self,base_url, api_key, model="gpt-4", temperature=0, max_tokens=4096, batch_size=None, enable_thinking=False, only_evaluate=False):
        """Initialize the prompt optimizer"""
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.base_url = base_url
        self.api_key = api_key
        self.advanceClient = OpenAI(base_url=cfg.ADVANCED_BASE_URL, api_key=cfg.ADVANCED_MODEL_API) #
        self.only_evaluate = only_evaluate
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.misclassified_examples = []
        self.current_prompt = ""
        self.enable_thinking = enable_thinking
        self.batch_size = batch_size

    def load_data(self, csv_path):
        """Load and parse the CSV data"""
        self.df = pd.read_csv(csv_path)
        print(f"Loaded {len(self.df)} examples")
        return self.df

    def set_prompt(self, prompt_template):
        """Set the current prompt template"""
        self.current_prompt = prompt_template

    def create_function_call_review(self, formatted_prompt) -> dict:
        tools = [{
            "type": "function",
            "function": {
                "name": "review_analysis",
                "description": "HTTP Attack Traffic Classification Result Review",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "review_analysis": {
                            "type": "string",
                            "description": "Your analysis for the review"
                        },
                        "review_result": {
                            "type": "string",
                            "enum": ["SUCCESS", "FAILURE", "UNKNOWN"],
                            "description": "You think the HTTP Attack Traffic Classification is what from the another analyst output"
                        }
                    },
                    "required": ["review_analysis", "review_result"]
                }
            }
        }]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": formatted_prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "review_analysis"}}
            # extra_body={"chat_template_kwargs": {"enable_thinking": False}} if not self.enable_thinking else None,
        )

        tool_call = response.choices[0].message.tool_calls[0]
        function_args = json.loads(tool_call.function.arguments)

        return {'review_result': function_args['review_result'], 'review_analysis': function_args['review_analysis']}

    def create_chat_response(self, formatted_prompt):
        payload = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": formatted_prompt
                }
            ],
            "model": self.model,
            "temperature": 0,
        })
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        url = "https://yunwu.ai/v1/chat/completions"
        retries = 1
        while True:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code != 200:
                print(f"Got an error: {response.status_code}, starting {retries} retry...")
                retries += 1
                time.sleep(1)
            else:
                break
        text = response.json()['choices'][0]['message']['content']

        return text

    def create_function_call(self, formatted_prompt) -> dict:
        tools = [{
            "type": "function",
            "function": {
                "name": "security_analysis",
                "description": "HTTP Attack Traffic Classification",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reason": {
                            "type": "string",
                            "description": "the reason of analysis"
                        },
                        "label": {
                            "type": "string",
                            "enum": ["SUCCESS", "FAILURE", "UNKNOWN"],
                            "description": "Analysis result label"
                        }
                    },
                    "required": ["reason", "label"]
                }
            }
        }]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "security_analysis"}}
            # extra_body={"chat_template_kwargs": {"enable_thinking": False}} if not self.enable_thinking else None,
        )

        tool_call = response.choices[0].message.tool_calls[0]
        function_args = json.loads(tool_call.function.arguments)

        return {'reason':function_args['reason'], 'label':function_args['label']}


    def evaluate_prompt(self, save_file, sample_size=None, examples=None, review_prompt=None, unlabeled_data=False):
        """Evaluate current prompt on labeled data"""
        if examples is None:
            if sample_size is None or sample_size >= len(self.df):
                examples = self.df
            else:
                examples = self.df.sample(sample_size)

        predictions = []
        true_labels = []
        self.misclassified_examples = []

        df = self.df.sample(n=8000)
        num_rows = len(df)
        if self.batch_size:
            num_batches = math.ceil(num_rows / self.batch_size)

        with open(save_file + ".jsonl", 'w', encoding='utf-8') as f_out:
            for i in tqdm(range(0, num_rows, self.batch_size), ncols=80):
                start_idx = i
                end_idx = min(i + self.batch_size, num_rows)  # 确保不会超出 DataFrame 边界

                # 获取当前批次的数据
                batch_df = df.iloc[start_idx:end_idx]

                batch_json = batch_df.to_json(orient="records")
                # Format the prompt with the current example
                template = Template(self.current_prompt)
                formatted_prompt = template.render(traffic_exchanges_list_json=batch_json)

                # if not self.enable_thinking:
                #     formatted_prompt += "\n /no_think"

                # Call the LLM API
                try:
                    # completion = self.client.chat.completions.create(
                    #     model=self.model,
                    #     messages=[{"role": "system", "content": formatted_prompt}],
                    #     temperature=self.temperature,
                    #     max_tokens=self.max_tokens,
                    #     #extra_body={"chat_template_kwargs": {"enable_thinking": False}} if not self.enable_thinking else None,
                    # )
                    #
                    # llm_output = completion.choices[0].message.content

                    llm_output = self.create_chat_response(formatted_prompt)
                    json_content_string = llm_output.replace('```json', '', 1).replace('```', '', 1).strip()
                    data_list = json.loads(json_content_string)
                    if unlabeled_data:
                        for record in data_list:
                            json.dump(record, f_out, ensure_ascii=False)  # ensure_ascii=False for non-ASCII chars
                            f_out.write('\n')
                            f_out.flush()
                    else:
                        for record in data_list:
                            json.dump(record, f_out, ensure_ascii=False)  # ensure_ascii=False for non-ASCII chars
                            f_out.write('\n')
                            f_out.flush()

                            if "SUCCESS" in record["label"]:
                                prediction = "SUCCESS"
                            elif "FAILURE" in record["label"]:
                                prediction = "FAILURE"
                            else:
                                prediction = "UNKNOWN"

                            row = batch_df[batch_df['uuid'] == record["uuid"]]
                            if row.empty:
                                print(f"Warning: UUID {record['uuid']} from LLM not found in original batch_df.")
                                continue
                            true_label = str(row['label'].iloc[0])
                            true_labels.append(true_label)
                            predictions.append(prediction)
                            if prediction != true_label:
                                mis_json = {
                                    "uuid": record.get('uuid'),
                                    "row": row.to_dict(orient='records'),
                                    "true_label": true_label,
                                    "predicted_label": prediction,
                                    "llm_output": record
                                }
                                json.dump(mis_json, f_out, ensure_ascii=False)
                                f_out.write('\n')
                                f_out.flush()



                    # review_output = {"label": "", "reason":""}
                    # if review_prompt:
                    #     review_template = Template(review_prompt)
                    #     fmt_review_prompt = review_template.render(req=req, rsp=rsp, llm_output=llm_output)
                    #     # if not self.enable_thinking:
                    #     #     fmt_review_prompt += "\n /no_think"
                    #     review_output = self.create_function_call_review(fmt_review_prompt)
                    #     if "SUCCESS" in review_output["review_result"]:
                    #         prediction = "SUCCESS"
                    #     elif "FAILURE" in review_output["review_result"]:
                    #         prediction = "FAILURE"
                    #     else:
                    #         prediction = "UNKNOWN"



                    #


                    # To avoid rate limiting
                    time.sleep(0.5)

                except Exception as e:
                    print(f"Error processing example {i}: {e}")

        # Calculate metrics
        accuracy = accuracy_score(true_labels, predictions)
        report = classification_report(true_labels, predictions, output_dict=True)
        conf_matrix = confusion_matrix(true_labels, predictions, labels=["SUCCESS", "FAILURE", "UNKNOWN"])

        metrics = {
            "accuracy": accuracy,
            "classification_report": report,
            "confusion_matrix": conf_matrix.tolist(),
            "misclassified_examples": self.misclassified_examples,
            "prompt": self.current_prompt
        }

        print(f"Accuracy: {accuracy:.4f}")
        print("Classification Report:")
        print(classification_report(true_labels, predictions))
        print("Confusion Matrix:")
        print(conf_matrix)
        print(f"Misclassified examples: {len(self.misclassified_examples)}/{len(examples)}")

        return metrics

    def get_misclassified(self):
        """Return all misclassified examples"""
        return self.misclassified_examples

    def suggest_improvements(self, num_learn = 5):
        """Use the LLM to suggest improvements to the prompt based on misclassifications"""
        num_learn = len(self.misclassified_examples) if num_learn >  len(self.misclassified_examples) else num_learn

        if not self.misclassified_examples:
            return "No misclassified examples to analyze."

        # Prepare examples for the LLM
        examples_text = ""
        for i, example in enumerate(self.misclassified_examples[:num_learn]):  # Limit to first 3 examples
            examples_text += f"Example {i + 1}:\n"
            examples_text += f"Request: {example['request']}\n"
            examples_text += f"Response: {example['response']}\n"
            examples_text += f"True label: {example['true_label']}\n"
            examples_text += f"Predicted label: {example['predicted_label']}\n\n"

        improvement_prompt = f"""
You are an expert in prompt engineering for security traffic classification. 
I'm using the following prompt template to classify HTTP traffic:

---
{self.current_prompt}
---

However, there are some misclassifications. Here are some examples that were incorrectly classified:

{examples_text}

Based on these misclassifications, suggest specific improvements to the prompt template. 
Focus on:
1. Making the classification criteria more precise
2. Adding relevant examples or patterns to look for
3. Providing better guidance on edge cases
4. Any structural improvements to the prompt

Provide a revised prompt template that should improve accuracy.
        """

        try:
            completion = self.advanceClient.chat.completions.create(
                model=cfg.ADVANCED_MODEL,
                messages=[{"role": "system", "content": improvement_prompt}],
                temperature=0.7,
                max_tokens=self.max_tokens
            )

            return completion.choices[0].message.content

        except Exception as e:
            return f"Error generating improvement suggestions: {e}"

    def iterative_optimization(self, iterations=3, sample_size=None):
        """Run multiple iterations of evaluation and improvement"""
        results = []

        for i in range(iterations):
            print(f"\n=== Iteration {i + 1}/{iterations} ===")

            # Evaluate the current prompt
            metrics = self.evaluate_prompt(sample_size)

            # Get suggestions for improvement
            suggestions = self.suggest_improvements()

            # Extract the revised prompt from suggestions (assuming it's properly formatted)
            try:
                # Very basic extraction - in practice, you might need more robust parsing
                # start_idx = suggestions.find("```") + 3
                # end_idx = suggestions.rfind("```")
                # if start_idx > 3 and end_idx > start_idx:
                #     revised_prompt = suggestions[start_idx:end_idx].strip()
                #     self.current_prompt = revised_prompt
                revised_prompt =  re.sub(r'<think>[\s\S]*?</think>\s*', '', suggestions).strip()


                results.append({
                    "iteration": i + 1,
                    "metrics": metrics,
                    "prompt": self.current_prompt,
                    "misclassified": self.misclassified_examples,
                    "suggestions": revised_prompt
                })

                self.current_prompt = revised_prompt

                print("\nRevised Prompt:")
                print(f"{revised_prompt[:300]}...")  # print the first 300 chars
            except:
                print("Could not extract a revised prompt. Using manual intervention.")


            # Save the current state
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.save_results(f"optimization_results_iter_{i + 1}_{timestamp}.json", results[-1])

        return results

    def save_results(self, filename, results):
        """Save results to a file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to {filename}")


@click.group()
def cli():
    """提示词优化工具 - 针对Web安全检测场景"""
    pass


def save_with_timestamp(data, suffix="data", directory=".", extension="json"):
    """
    将JSON数据保存到以当前时间命名的文件中

    参数:
        data: 要保存的JSON数据/对象
        prefix: 文件名前缀（可选）
        directory: 保存目录（可选）
        extension: 文件扩展名（可选）

    返回:
        保存的文件路径
    """
    # 确保目录存在
    os.makedirs(directory, exist_ok=True)

    # 获取当前时间并格式化为文件名
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # 构建文件名
    filename = f"{timestamp}_{suffix}.{extension}"
    filepath = os.path.join(directory, filename)

    if extension == "json" or extension == "txt":
        # 写入JSON数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        raise NotImplementedError

    return filepath


# 获取当前文件目录的上一层目录
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("project path: ", PROJECT_PATH)

@cli.command("optimize")
@click.option('--data_file', default=f"{PROJECT_PATH}/demo_data/labeled_demo_data_aitmg_202504.csv", help=f"train data path, default demo_data/labeled_demo_data_aitmg_202504.csv")
@click.option('--prompt', default=f"{PROJECT_PATH}/prompt/initial_prompt.md", help=f"想要调优提示词的路径，默认是 prompt/initial_prompt.md")
@click.option('--model', default=cfg.DEFAULT_MODEL, help=f'使用的模型，默认cfg.DEFAULT_MODEL: {cfg.DEFAULT_MODEL}')
@click.option('--base_url',default=cfg.SGLANG_ENDPOINT, help=f'模型的base_url，默认cfg.SGLANG_ENDPOINT: {cfg.SGLANG_ENDPOINT}')
@click.option('--api_key', '-k',default=cfg.API_KEY, help=f'api_key，默认cfg.API_KEY: {cfg.API_KEY}')
@click.option('--temperature', '-t', type=float, default=cfg.DEFAULT_TEMPERATURE, help='温度参数，默认: 0.0')
@click.option('--max_tokens', '-m', type=int, default=4096, help='最大生成token数，默认: 4096')
@click.option('--only_evaluate', '-e', is_flag=True, default=False, help='是否仅执行评估，不执行优化')
@click.option('--optimization_iterations', '-i', type=int, default=3, help='优化迭代次数，默认: 3')
@click.option('--output_dir', '-o', default=f"{PROJECT_PATH}/result", help='输出目录, 默认 result')
@click.option('--sample_size', type=int, default=None, help='读取数据集中多少条数据进行训练')
@click.option('--review_prompt', default=None, help='review prompt')
@click.option('--batch_size', default=1, help='模型一次处理的批大小')
@click.option('--unlabeled_data', is_flag=True, default=False, help='是否仅执行评估，不执行优化')
def optimize_prompts(data_file, prompt, model, base_url, api_key, temperature, max_tokens, only_evaluate, optimization_iterations, output_dir,sample_size, review_prompt, batch_size, unlabeled_data):
    """优化流量检测的提示词"""
    # Initial prompt template
    prompt_path = os.path.join(PROJECT_PATH, "prompt", prompt)
    with open(prompt_path, 'r', encoding='utf-8') as f:
        initial_prompt = f.read()

    # Create the optimizer
    optimizer = PromptOptimizer(base_url=base_url,
                                api_key=api_key,
                                model=model,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                only_evaluate = only_evaluate,
                                batch_size=batch_size
                                )
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filePathNoExtension = os.path.join(output_dir, timestamp)
    # Load data
    optimizer.load_data(data_file)

    # Set the initial prompt
    optimizer.set_prompt(initial_prompt)

    if only_evaluate:
        if review_prompt:
            review_prompt_path = os.path.join(PROJECT_PATH, "prompt", review_prompt)
            with open(review_prompt_path, 'r', encoding='utf-8') as f:
                review_prompt = f.read()


        # Run a single evaluation
        metrics = optimizer.evaluate_prompt(filePathNoExtension, sample_size=sample_size, review_prompt =review_prompt, unlabeled_data=unlabeled_data)

        # Get misclassified examples
        misclassified = optimizer.get_misclassified()
        print(f"Found {len(misclassified)} misclassified examples")

        save_with_timestamp(metrics, str(metrics["accuracy"]), directory=output_dir, extension="txt")
        save_with_timestamp(metrics, str(metrics["accuracy"]), directory=output_dir, extension="json")

    else:
        # Run iterative optimization (optional)
        results = optimizer.iterative_optimization(iterations=optimization_iterations, sample_size=sample_size)
        save_with_timestamp(results, "prompt", directory=output_dir, extension="txt")
        save_with_timestamp(results, "prompt", directory=output_dir, extension="json")

# Example usage
if __name__ == "__main__":
    cli()
