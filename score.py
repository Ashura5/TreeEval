import json
from tqdm import tqdm
import pandas as pd
import numpy as np


def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in tqdm(f)]


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.loads(f.read())


def dump_jsonl(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for line in tqdm(data):
            f.write(json.dumps(line, ensure_ascii=False) + "\n")


def remove_outliers(arr):
    # Extract the first element from each sub-list
    first_elements = [item[0] for item in arr]
    if all(x >= 2.5 for x in first_elements) or all(x <= 2.5 for x in first_elements):
        return 2
    else:
        return 0.5



def count_question_num(data) -> float:
    res = 0
    if len(data["question"]) != 0:
        res = 1
    if len(data["children"]) != 0:
        for child in data["children"]:
            res = res + count_question_num(child)
    return res


def is_leaf(data) -> bool:
    if len(data["children"]) == 0:
        return True
    for child in data["children"]:
        if len(child["question"]) == 0:
            return True
    return False


def has_leaf_child(data) -> bool:
    for child in data["children"]:
        if is_leaf(child):
            return True
    return False


def compute(data, lenth=0, w_3=1):
    """
    Computes a value based on the given data.

    Parameters:
    data (dict): A dictionary containing the data for computation.

    Returns:
    tuple: A tuple containing the computed value, maximum depth, and power.

    """
    lenth = lenth + 1
    if is_leaf(data):
        w_1 = 1 / lenth
        if data["topic_from"] == "both":
            w_2 = 2
        elif data["topic_from"] == "lchild" and data["question_type"] == "Response 2":
            w_2 = 2
        elif data["topic_from"] == "rchild" and data["question_type"] == "Response 1":
            w_2 = 2
        else:
            w_2 = 1
        w = w_1 * w_2 * w_3
        if data["question_type"] == "Response 1":
            return 5 * w, w
        elif data["question_type"] == "Response 2":
            return 0, w
        else:
            return 2.5 * w, w
    if has_leaf_child(data):
        x = []
        for child in data["children"]:
            if child["question_type"] == "Response 1":
                x.append(1)
            elif child["question_type"] == "Response 2":
                x.append(-1)
            else:
                x.append(0)
        mean = sum(x) / len(x)

        variance = sum((i - mean) ** 2 for i in x) / len(x)
        w_3 = 1 / (2 * variance + 1)
    s_all = 0
    w_all = 0
    for child in data["children"]:
        score, weight = compute(child, lenth, w_3)
        s_all = s_all + score
        w_all = w_all + weight
    return s_all, w_all


def compute_without_root(data, lenth=0, w_3=1):
    """
    Computes a value based on the given data.

    Parameters:
    data (dict): A dictionary containing the data for computation.

    Returns:
    tuple: A tuple containing the computed value, maximum depth, and power.

    """
    lenth = lenth + 1
    if is_leaf(data):
        w_1 = 1 / lenth
        if data["topic_from"] == "both":
            w_2 = 2
        elif data["topic_from"] == "lchild" and data["question_type"] == "Response 2":
            w_2 = 2
        elif data["topic_from"] == "rchild" and data["question_type"] == "Response 1":
            w_2 = 2
        else:
            w_2 = 1
        w = w_2 * w_3
        if data["question_type"] == "Response 1":
            return 5 * w, w
        elif data["question_type"] == "Response 2":
            return 0, w
        else:
            return 2.5 * w, w
    if has_leaf_child(data):
        x = []
        for child in data["children"]:
            if child["question_type"] == "Response 1":
                x.append(1)
            elif child["question_type"] == "Response 2":
                x.append(-1)
            else:
                x.append(0)
        mean = sum(x) / len(x)

        variance = sum((i - mean) ** 2 for i in x) / len(x)
        w_3 = 1 / (2 * variance + 1)
    s_all = 0
    w_all = 0
    for child in data["children"]:
        score, weight = compute_without_root(child, lenth, w_3)
        s_all = s_all + score
        w_all = w_all + weight
    return s_all, w_all


def compute_without_topic(data, lenth=0, w_3=1):
    """
    Computes a value based on the given data.

    Parameters:
    data (dict): A dictionary containing the data for computation.

    Returns:
    tuple: A tuple containing the computed value, maximum depth, and power.

    """
    lenth = lenth + 1
    if is_leaf(data):
        w_1 = 1 / lenth
        if data["topic_from"] == "both":
            w_2 = 2
        elif data["topic_from"] == "lchild" and data["question_type"] == "Response 2":
            w_2 = 2
        elif data["topic_from"] == "rchild" and data["question_type"] == "Response 1":
            w_2 = 2
        else:
            w_2 = 1
        w = w_1 * w_3
        if data["question_type"] == "Response 1":
            return 5 * w, w
        elif data["question_type"] == "Response 2":
            return 0, w
        else:
            return 2.5 * w, w
    if has_leaf_child(data):
        x = []
        for child in data["children"]:
            if child["question_type"] == "Response 1":
                x.append(1)
            elif child["question_type"] == "Response 2":
                x.append(-1)
            else:
                x.append(0)
        mean = sum(x) / len(x)

        variance = sum((i - mean) ** 2 for i in x) / len(x)
        w_3 = 1 / (2 * variance + 1)
    s_all = 0
    w_all = 0
    for child in data["children"]:
        score, weight = compute_without_topic(child, lenth, w_3)
        s_all = s_all + score
        w_all = w_all + weight
    return s_all, w_all


def compute_without_sibling(data, lenth=0, w_3=1):
    """
    Computes a value based on the given data.

    Parameters:
    data (dict): A dictionary containing the data for computation.

    Returns:
    tuple: A tuple containing the computed value, maximum depth, and power.

    """
    lenth = lenth + 1
    if is_leaf(data):
        w_1 = 1 / lenth
        if data["topic_from"] == "both":
            w_2 = 2
        elif data["topic_from"] == "lchild" and data["question_type"] == "Response 2":
            w_2 = 2
        elif data["topic_from"] == "rchild" and data["question_type"] == "Response 1":
            w_2 = 2
        else:
            w_2 = 1
        w = w_1 * w_2
        if data["question_type"] == "Response 1":
            return 5 * w, w
        elif data["question_type"] == "Response 2":
            return 0, w
        else:
            return 2.5 * w, w
    if has_leaf_child(data):
        x = []
        for child in data["children"]:
            if child["question_type"] == "Response 1":
                x.append(1)
            elif child["question_type"] == "Response 2":
                x.append(-1)
            else:
                x.append(0)
        mean = sum(x) / len(x)

        variance = sum((i - mean) ** 2 for i in x) / len(x)
        w_3 = 1 / (2 * variance + 1)
    s_all = 0
    w_all = 0
    for child in data["children"]:
        score, weight = compute_without_sibling(child, lenth, w_3)
        s_all = s_all + score
        w_all = w_all + weight
    return s_all, w_all


def count_all(data):
    l = {}
    for key in data:
        l[key] = count_question_num(data[key])
    return l


def compute_all(data):
    l = {}
    for key in data:
        l[key] = compute(data[key])[0] / compute(data[key])[1]
        # print(key, l[key])
    return l


def compute_without_root_all(data):
    l = {}
    for key in data:
        l[key] = compute_without_root(data[key])[0] / compute_without_root(data[key])[1]
        # print(key, l[key])
    return l


def compute_without_topic_all(data):
    l = {}
    for key in data:
        l[key] = compute_without_topic(data[key])[0] / compute_without_topic(data[key])[1]
        # print(key, l[key])
    return l


def compute_without_sibling_all(data):
    l = {}
    for key in data:
        l[key] = compute_without_sibling(data[key])[0] / compute_without_sibling(data[key])[1]
        # print(key, l[key])
    return l


# compute_all(data)

import os

folder_path = "./output"
datas = []
model_list = [
    "Yi",
    "Xwin-LM-13B-V0.1",
    "Mistral",
    "vicuna-33b-v1.3",
    "WizardLM-13B-V1.2",
    "zephyr-7b-beta",
]
# 遍历文件夹下的所有文件
for filename in os.listdir(folder_path):
    # 拼接文件路径
    file_path = os.path.join(folder_path, filename)
    # 获取文件扩展名
    _, ext = os.path.splitext(filename)
    # 判断文件扩展名是否为.json
    if ext == ".json" and "_" in filename:
        # 打开文件并读取内容
        data = read_json(file_path)
        model1 = filename[:-5].split("_")[0]
        model2 = filename[:-6].split("_")[-1]

        count_data = count_all(data)
        score_data = compute_all(data)
        if model_list.index(model1) > model_list.index(model2):
            for key in score_data:
                score_data[key] = 5 - score_data[key]
            model1, model2 = model2, model1
        num_all = sum(count_data.values())
        score_avg = sum(score_data.values()) / len(score_data)
        data_entry = {
            "model1": model1,
            "model2": model2,
            "n": filename[-6],
            "number": num_all,  # 假设 num_avg 已在循环外部计算
            "score": score_avg,  # 假设 score_avg 已在循环外部计算
        }
        for key in count_data:
            data_entry["count_" + key] = count_data[key]
        for key in score_data:
            data_entry["score_" + key] = score_data[key]

        # 将更新后的 data_entry 添加到 datas 列表中
        datas.append(data_entry)
        # print(filename[:-6])
        # print(compute_all(data))
        # print(count_all(data))
sorted_lst = sorted(
    datas, key=lambda x: (model_list.index(x["model1"]), model_list.index(x["model2"]))
)

df = pd.DataFrame(sorted_lst)

# 将DataFrame写入Excel文件
df.to_excel(folder_path + "/result.xlsx", index=False)
