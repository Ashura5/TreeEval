import numpy as np
import common.utils as utils
import common.consts as consts
import actors.checker as checker


class LLMReplyParserBase(object):
    def __init__(self) -> None:
        pass

    def parse_llm_reply(self, llm_reply):
        pass


class LLMReplyParserForQuestion(LLMReplyParserBase):
    def __init__(self) -> None:
        pass

    def parse_llm_reply(
        self,
        topic,
        question,
        answer1,
        answer2,
        Subtopic1,
        Subtopic2,
        Eval_type_1,
        Eval_type_2,
    ):
        # eval_difficulty=utils.extract_difficulty_from_text_string(Eval_difficulty)
        eval_type_1 = utils.extract_type_from_text_string(Eval_type_1)
        eval_type_2 = utils.extract_type_from_text_string(Eval_type_2)
        if eval_type_1 == "Response 1":
            if eval_type_2 == "Response 1":
                eval_type = "Tie"
            else:
                eval_type = "Response 1"
        elif eval_type_1 == "Response 2":
            if eval_type_2 == "Response 2":
                eval_type = "Tie"
            else:
                eval_type = "Response 2"
        else:
            if eval_type_2 == "Response 2":
                eval_type = "Response 1"
            elif eval_type_2 == "Response 1":
                eval_type = "Response 2"
            else:
                eval_type = "Tie"
        sub1 = utils.extract_subtopic_from_text_string(Subtopic1)
        sub1, cos1 = utils.find_most_similar(answer1, sub1, 2)
        sub2 = utils.extract_subtopic_from_text_string(Subtopic2)
        sub2, cos2 = utils.find_most_similar(answer2, sub2, 2)
        # for i in range(len(cos2)):
        #     for j in range(len(cos1)):
        #         if utils.cosine_similarity(cos1[j],cos2[i])>=0.9:
        #             sub2[i]=sub1[j]
        #             cos2[i]=cos1[j]
        #             break
        # sub2=list(set(sub2))
        # flag_match=utils.test_match(eval_difficulty,eval_type)
        # if not flag_match:
        #     return checker.QuestionStateCheckResults(question,answer1,answer2,eval_difficulty,eval_type,False)
        return checker.QuestionStateCheckResults(
            topic, question, answer1, answer2, eval_type, sub1, sub2, "", True
        )

    def parse_llm_reply_2(
        self,
        topic,
        question,
        answer1,
        answer2,
        Subtopic1,
        Subtopic2,
        Eval_type_1,
        Eval_type_2,
    ):
        # eval_difficulty=utils.extract_difficulty_from_text_string(Eval_difficulty)
        eval_type_1 = utils.extract_type_from_text_string(Eval_type_1)
        eval_type_2 = utils.extract_type_from_text_string(Eval_type_2)
        if eval_type_1 == "Response 1":
            if eval_type_2 == "Response 1":
                eval_type = "Tie"
            else:
                eval_type = "Response 1"
        elif eval_type_1 == "Response 2":
            if eval_type_2 == "Response 2":
                eval_type = "Tie"
            else:
                eval_type = "Response 2"
        else:
            if eval_type_2 == "Response 2":
                eval_type = "Response 1"
            elif eval_type_2 == "Response 1":
                eval_type = "Response 2"
            else:
                eval_type = "Tie"
        if eval_type == "Response 1" or eval_type == "Response 2":
            return checker.QuestionStateCheckResults(
                topic, question, answer1, answer2, eval_type, [], [], "", True
            )
        sub1 = utils.extract_subtopic_from_text_string(Subtopic1)
        sub1, cos1 = utils.find_most_similar(answer1, sub1, 3)
        sub2 = utils.extract_subtopic_from_text_string(Subtopic2)
        sub2, cos2 = utils.find_most_similar(answer2, sub2, 3)
        # for i in range(len(cos2)):
        #     for j in range(len(cos1)):
        #         if utils.cosine_similarity(cos1[j],cos2[i])>=0.9:
        #             sub2[i]=sub1[j]
        #             cos2[i]=cos1[j]
        #             break
        # sub2=list(set(sub2))
        # flag_match=utils.test_match(eval_difficulty,eval_type)
        # if not flag_match:
        #     return checker.QuestionStateCheckResults(question,answer1,answer2,eval_difficulty,eval_type,False)
        return checker.QuestionStateCheckResults(
            topic, question, answer1, answer2, eval_type, sub1, sub2, "", True
        )
