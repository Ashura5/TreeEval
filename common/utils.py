import json
import re
import ast
import openai
import numpy as np


def cosine_similarity(vec_a, vec_b):
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    return dot_product / (norm_a * norm_b)


openai.api_type = "open_ai"
openai.api_base = "http://localhost:23261/v1"
openai.api_key = "Empty"
openai.api_version = None


def get_embedding(sentence):
    if len(sentence) > 500:
        sentence = sentence[:500]
    try:
        res = openai.Embedding.create(model="bge-large-en-v1.5", input=sentence)[
            "data"
        ][0]["embedding"]
    except:
        openai.api_type = "open_ai"
        openai.api_base = "http://localhost:23261/v1"
        openai.api_key = "Empty"
        openai.api_version = None
        res = openai.Embedding.create(model="bge-large-en-v1.5", input=sentence[:400])[
            "data"
        ][0]["embedding"]
    return res


def check_similarity(question, state, question_list, topic):
    em = get_embedding(question)
    topic_em = get_embedding(topic)
    if cosine_similarity(em, topic_em) < 0.6:
        return False, em
    for item in question_list:
        if len(state) > len(item["state"]):
            if item["state"] != state[: len(item["state"])]:
                similarity = cosine_similarity(em, item["embedding"])
                if similarity >= 0.82 and similarity <= 0.45:
                    return False, em
            else:
                similarity = cosine_similarity(em, item["embedding"])
                if similarity >= 0.9 and similarity <= 0.5:
                    return False, em
        else:
            similarity = cosine_similarity(em, item["embedding"])
            if similarity >= 0.82 and similarity <= 0.45:
                return False, em
    return True, em


def find_most_similar(answer, subtopics, k):
    embedding_q = get_embedding(answer)
    subtopics = list(set(subtopics))
    cos = [get_embedding(x) for x in subtopics]
    n_sub = []
    n_cos = []

    sim = [cosine_similarity(embedding_q, x) for x in cos]
    combined = sorted(zip(subtopics, cos, sim), key=lambda x: x[2], reverse=True)
    sub_n, cos_n, sim_n = zip(*combined)
    n_sub.append(sub_n[0])
    n_cos.append(cos_n[0])

    for i in range(min(len(subtopics), k) - 1):
        sub_n = list(sub_n[1:])
        cos_n = list(cos_n[1:])
        sim_n = list(sim_n[1:])
        for j in range(len(sim_n)):
            sim_n[j] = sim_n[j] - cosine_similarity(n_cos[-1], cos_n[j])
        combined_n = sorted(zip(sub_n, cos_n, sim_n), key=lambda x: x[2], reverse=True)
        sub_n, cos_n, sim_n = zip(*combined_n)
        n_sub.append(sub_n[0])
        n_cos.append(cos_n[0])

    return n_sub, n_cos


def find_least_similar_pair(lst):
    min_similarity = float("inf")
    least_similar_pair = []
    cos_similar_pair = []
    cos = [get_embedding(x) for x in lst]
    # 遍历列表中的每一对元素
    for i in range(len(cos)):
        for j in range(i + 1, len(cos)):
            similarity = cosine_similarity(cos[i], cos[j])
            if similarity < min_similarity:
                min_similarity = similarity
                least_similar_pair = [lst[i], lst[j]]
                cos_similar_pair = [cos[i], cos[j]]
    if len(least_similar_pair) == 0 and len(cos_similar_pair) == 0:
        return lst, cos
    return least_similar_pair, cos_similar_pair


def extract_json_from_text_string(text_str: str):
    try:
        lp_idx = text_str.index("{")
        rp_idx = text_str.rindex("}")
        json_str = text_str[lp_idx : rp_idx + 1]
        json_obj = json.loads(json_str)
        return True, json_obj
    except:
        return False, None


def extract_difficulty_from_text_string(text_str: str):
    try:
        new_text_str = "".join(
            char.lower() for char in text_str[-40:] if char.isalnum()
        )
        if "bothdifficult" in new_text_str:
            return "both difficult"
        if "botheasy" in new_text_str:
            return "both easy"
        if "easierfor1" in new_text_str:
            return "easier for 1"
        if "easierfor2" in new_text_str:
            return "easier for 2"
        return "None"
    except:
        return "None"


def extract_subtopic_from_text_string(text_str):
    # 匹配括号内的内容
    if isinstance(text_str, list):
        return text_str
    pattern = r"\[([^\[\]]+)\]"
    matches = re.findall(pattern, text_str)

    # 初始化lst为空列表
    lst = []

    # 如果匹配到括号内的内容
    if matches:
        lst_str = matches[-1]
        try:
            lst = ast.literal_eval(lst_str)
        except:
            lst = [x.strip() for x in lst_str.split(",")]
    else:
        # 检查不同格式的列表
        numbered_items_colon = re.findall(r"\d+\.\s*([^:]+):", text_str)
        numbered_items_simple = re.findall(r"\d+\.\s*([^\d\.\s]+)", text_str)
        dash_items = re.findall(r"\-\s*([\w\s]+)", text_str)

        # 选择最长的列表
        longest_list = max(
            [dash_items, numbered_items_colon, numbered_items_simple], key=len
        )
        if longest_list:
            lst = [x.strip() for x in longest_list]
        else:
            # 使用引号或换行符进行切分
            lst = re.split(r"\'|\"|\n", text_str)
            lst = [x.strip() for x in lst if x.strip() and x.strip() != ","]

    # 将提取的项目转换为小写
    if isinstance(lst, str):
        lst = [lst]
    if isinstance(lst, dict):
        lst = list(lst.values())
    lst = [str(x).lower() for x in lst]
    return lst


def find_str(s, s1, s2):
    pos1 = s.rfind(s1)
    pos2 = s.rfind(s2)
    if pos1 == -1 and pos2 == -1:
        return "tie"
    elif pos1 == -1:
        return s2
    elif pos2 == -1:
        return s1
    else:
        return s2 if pos2 > pos1 else s1


def extract_type_from_text_string(text_str: str):
    try:
        if "question_type" in text_str:
            new_text_str = text_str.split("question_type")[-1]
            new_text_str = "".join(
                char.lower() for char in new_text_str if char.isalnum()
            )
        else:
            new_text_str = "".join(char.lower() for char in text_str if char.isalnum())
        res = find_str(new_text_str, "response1", "response2")
        if "response1" == res:
            return "Response 1"
        if "response2" == res:
            return "Response 2"
        if "tie" == res:
            return "Tie"
        return "Tie"
    except:
        return "Tie"


def test_match(difficulty, type):
    if difficulty == "both difficult" or difficulty == "both easy":
        if type == "Tie":
            return True
        return False
    if difficulty == "easier for 1" and type == "Response 1":
        return True
    if difficulty == "easier for 2" and type == "Response 2":
        return True
    return False
