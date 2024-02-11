import sys
from common.config import Config
from tot.tot_question import TreeOfThoughtQuestion
import json
from random import sample
import time
from tqdm import tqdm


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print("""Usage:""")
        print("""    python main.py model1 model2 """)
        print("""Example:""")
        print("""    python main.py zephyr-7b-beta Xwin-LM-7B-V0.2""")
        print("""    python main.py Mistral vicuna-7b-v1.5 """)
        exit(1)

    model1 = sys.argv[1]
    model2 = sys.argv[2]
    print(model1, model2)
    path_to_config_question_yaml = "./config.yaml"
    config_question = Config(path_to_config_question_yaml)

    path_to_config_answer1_yaml = "./config_" + model1 + ".yaml"
    config_answer1 = Config(path_to_config_answer1_yaml)

    path_to_config_answer2_yaml = "./config_" + model2 + ".yaml"
    config_answer2 = Config(path_to_config_answer2_yaml)

    path_to_config_eval_yaml = "./config.yaml"
    config_eval = Config(path_to_config_eval_yaml)

    path_to_config_topic_yaml = "./config.yaml"
    config_topic = Config(path_to_config_topic_yaml)

    tot = TreeOfThoughtQuestion(
        config_question, config_answer1, config_answer2, config_eval, config_topic
    )

    user_input_list = [
        "Entertainment & Leisure",
        "Health & Lifestyle",
        "Education & Information",
        "Business & Finance",
        "Technology & Communication",
        "Society & Government",
        "Travel & Shopping",
    ]

    user_input_list = [item.replace(" ", "_") for item in user_input_list]

    input_list = user_input_list
    for i in range(3):
        question_list = {}
        start = time.time()
        for u in tqdm(input_list):
            success, solution, question_dict = tot.run(u)
            question_list[u] = question_dict
        with open("./output/" + model1 + "_" + model2 + str(i) + ".json", "w") as f:
            json.dump(question_list, f)
        end = time.time()
        print(end - start)

