import pandas as pd

# 创建一个示例 DataFrame
data = {
    'product_id': [101, 102, 103, 104, 105, 106, 107, 108],
    'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Webcam', 'Speaker', 'Printer', 'Scanner'],
    'category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Accessories', 'Accessories', 'Peripherals', 'Peripherals'],
    'price': [1200, 25, 75, 300, 50, 150, 400, 250],
    'in_stock': [True, True, False, True, True, False, True, True]
}
df = pd.DataFrame(data)

print("原始 DataFrame:")
print(df)
print("-" * 50)

# 假设我们设置 'product_id' 为索引
df_indexed = df.set_index('product_id')
print("\n设置 'product_id' 为索引后的 DataFrame:")
print(df_indexed)
print("-" * 50)

# 使用 .loc 查找 product_id 为 103 的行
row_by_id = df_indexed.loc[103]
print("\n使用 .loc 查找 product_id 为 103 的行:")
print(row_by_id)
print("-" * 50)

# 如果索引是默认的整数索引，loc 也可以用整数
row_by_default_index = df.loc[1] # 查找原始 DataFrame 中索引为 1 的行
print("\n使用 .loc 查找原始 DataFrame 中索引为 1 的行:")
print(row_by_default_index)
print("-" * 50)
