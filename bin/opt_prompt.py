from datetime import datetime
from email.policy import default
from openai import OpenAI
import click
import pandas as pd
import json
import os
import openai
import time
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np
import sys
from jinja2 import Template

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.generator import generate
    from src.client import create_client
    import config.setting as cfg
except ImportError:
    print("无法导入项目模块，请确保您在项目根目录下运行此脚本")
    sys.exit(1)


class PromptOptimizer:
    def __init__(self,base_url, api_key, model="gpt-4", temperature=0, max_tokens=4096):
        """Initialize the prompt optimizer"""
        self.client = OpenAI(base_url=base_url, api_key=api_key)

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.misclassified_examples = []
        self.current_prompt = ""

    def load_data(self, csv_path):
        """Load and parse the CSV data"""
        self.df = pd.read_csv(csv_path)
        print(f"Loaded {len(self.df)} examples")
        return self.df

    def set_prompt(self, prompt_template):
        """Set the current prompt template"""
        self.current_prompt = prompt_template

    def evaluate_prompt(self, sample_size=None, examples=None):
        """Evaluate current prompt on labeled data"""
        if examples is None:
            if sample_size is None or sample_size >= len(self.df):
                examples = self.df
            else:
                examples = self.df.sample(sample_size)

        predictions = []
        true_labels = []
        self.misclassified_examples = []

        for idx, row in examples.iterrows():
            request = row['req']
            response = row['rsp']
            true_label = row['label']

            # Format the prompt with the current example
            template = Template(self.current_prompt)
            formatted_prompt = template.render(request=request, response=response)

            # Call the LLM API
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": formatted_prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

                llm_output = completion.choices[0].message.content

                # Extract the classification from the output
                if "SUCCESS" in llm_output:
                    prediction = "SUCCESS"
                elif "FAILURE" in llm_output:
                    prediction = "FAILURE"
                else:
                    prediction = "UNKNOWN"

                predictions.append(prediction)
                true_labels.append(true_label)

                if prediction != true_label:
                    self.misclassified_examples.append({
                        "uuid": row.get('uuid', idx),
                        "request": request,
                        "response": response,
                        "true_label": true_label,
                        "predicted_label": prediction,
                        "llm_output": llm_output
                    })

                # To avoid rate limiting
                time.sleep(0.5)

            except Exception as e:
                print(f"Error processing example {idx}: {e}")

        # Calculate metrics
        accuracy = accuracy_score(true_labels, predictions)
        report = classification_report(true_labels, predictions, output_dict=True)
        conf_matrix = confusion_matrix(true_labels, predictions, labels=["SUCCESS", "FAILURE", "UNKNOWN"])

        metrics = {
            "accuracy": accuracy,
            "classification_report": report,
            "confusion_matrix": conf_matrix.tolist()
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
            completion = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": improvement_prompt}],
                temperature=0.7,
                max_tokens=1500
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
                start_idx = suggestions.find("```") + 3
                end_idx = suggestions.rfind("```")
                if start_idx > 3 and end_idx > start_idx:
                    revised_prompt = suggestions[start_idx:end_idx].strip()
                    self.current_prompt = revised_prompt

                print("\nRevised Prompt:")
                print(f"{revised_prompt[:300]}...")  # print the first 300 chars
            except:
                print("Could not extract a revised prompt. Using manual intervention.")

            results.append({
                "iteration": i + 1,
                "metrics": metrics,
                "misclassified": self.misclassified_examples,
                "suggestions": suggestions
            })

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

    if extension == "json":
        # 写入JSON数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)

    return filepath


# 获取当前文件目录的上一层目录
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("project path: ", PROJECT_PATH)

@cli.command("optimize")
@click.option('--data_file', default=f"{PROJECT_PATH}/demo_data/labeled_demo_data_aitmg_202504.csv", help=f"train data path, default demo_data/labeled_demo_data_aitmg_202504.csv")
@click.option('--initial_prompt_path', default=f"{PROJECT_PATH}/prompt/initial_prompt.md", help=f"想要调优提示词的路径，默认是 prompt/initial_prompt.md")
@click.option('--model', default=cfg.DEFAULT_MODEL, help=f'使用的模型，默认cfg.DEFAULT_MODEL: {cfg.DEFAULT_MODEL}')
@click.option('--base_url',default=cfg.SGLANG_ENDPOINT, help=f'模型的base_url，默认cfg.SGLANG_ENDPOINT: {cfg.SGLANG_ENDPOINT}')
@click.option('--api_key', '-k',default=cfg.API_KEY, help=f'api_key，默认cfg.API_KEY: {cfg.API_KEY}')
@click.option('--temperature', '-t', type=float, default=cfg.DEFAULT_TEMPERATURE, help='温度参数，默认: 0.0')
@click.option('--max_tokens', '-m', type=int, default=4096, help='最大生成token数，默认: 4096')
@click.option('--only-evaluate', '-e', is_flag=True, default=False, help='是否仅执行评估，不执行优化')
@click.option('--optimization_iterations', '-i', type=int, default=3, help='优化迭代次数，默认: 3')
@click.option('--output_dir', '-o', default=f"{PROJECT_PATH}/result", help='输出目录, 默认 result')
def optimize_prompts(data_file, initial_prompt_path, model, base_url, api_key, temperature, max_tokens, only_evaluate, optimization_iterations, output_dir):
    """优化流量检测的提示词"""
    # Initial prompt template
    with open(initial_prompt_path, 'r', encoding='utf-8') as f:
        initial_prompt = f.read()

    # Create the optimizer
    optimizer = PromptOptimizer(base_url=base_url,
                                api_key=api_key,
                                model=model,
                                temperature=temperature,
                                max_tokens=max_tokens)

    # Load data
    optimizer.load_data(data_file)

    # Set the initial prompt
    optimizer.set_prompt(initial_prompt)

    if only_evaluate:
        # Run a single evaluation
        metrics = optimizer.evaluate_prompt()

        # Get misclassified examples
        misclassified = optimizer.get_misclassified()
        print(f"Found {len(misclassified)} misclassified examples")

        save_with_timestamp(metrics, str(metrics["accuracy"]), extension="txt")
        save_with_timestamp(metrics, str(metrics["accuracy"]), extension="json")

    else:
        # Run iterative optimization (optional)
        results = optimizer.iterative_optimization(iterations=optimization_iterations)
        save_with_timestamp(results, "prompt", extension="txt")
        save_with_timestamp(results, "prompt", extension="json")

# Example usage
if __name__ == "__main__":
    cli()
