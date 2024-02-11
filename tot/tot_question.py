import json
import common.consts as consts
import common.utils as utils
from common.enums import *
from common.hyperparams import HyperParams
from actors.state import QuestionStateManager
from actors.llm import LLMAgent
from actors.parser import LLMReplyParserForQuestion
from actors.prompter import QuestionPrompter
from actors.prompter import AnswerPrompter
from actors.prompter import EvalPrompter
import copy
from common.utils import check_similarity

# from modelscope.pipelines import pipeline
# from modelscope.utils.constant import Tasks

# def split_text_uniformly(answer, max_length=256):
#     if len(answer) <= max_length:
#         return [answer]
#     segments = []
#     current_segment = []
#     current_length = 0
#     for word in answer.split():  # Assuming whitespace tokenization; adjust as needed
#         word_length = len(word) + 1  # Adding 1 for the space
#         if current_length + word_length > max_length:
#             segments.append(" ".join(current_segment))
#             current_segment = [word]
#             current_length = word_length
#         else:
#             current_segment.append(word)
#             current_length += word_length

#     # Don't forget to add the last segment if it's not empty
#     if current_segment:
#         segments.append(" ".join(current_segment))
#     return segments


class TreeOfThoughtQuestion(object):
    def __init__(
        self,
        config_question,
        config_answer1,
        config_answer2,
        config_eval,
        config_subtopic,
    ) -> None:
        self.config_question = config_question
        self.config_answer1 = config_answer1
        self.config_answer2 = config_answer2
        self.config_eval = config_eval
        self.config_subtopic = config_subtopic
        self.llm_agent = LLMAgent(config_question)
        self.llm1 = LLMAgent(config_answer1)
        self.llm2 = LLMAgent(config_answer2)
        self.eval_agent = LLMAgent(config_eval)
        self.topic_agent = LLMAgent(config_subtopic)
        # self.ner_pipeline = pipeline(Tasks.named_entity_recognition, '/mnt/nj-1/usr/lixiang/LLMs/ner-english',device="cuda:7")

    def run(self, user_input):
        max_num_rounds = HyperParams.MaxNumConversationRounds
        totExecutor = TreeOfThoughtExecutorForQuestion(
            self.config_question,
            self.config_answer1,
            self.config_answer2,
            self.config_eval,
            self.config_subtopic,
            # self.ner_pipeline
        )
        result, history, question_dict = totExecutor.run(user_input, max_num_rounds)
        return result, history, question_dict


class TreeOfThoughtExecutorBase(object):
    def __init__(self) -> None:
        self.conversation_history = ""
        self.state_manager_visit_count_map = {}

    def _incr_state_visit_count(self):
        if self.state_manager.get_current_state() is None:
            return
        curr_question = self.state_manager.get_current_state().topic
        if not (curr_question in self.state_manager_visit_count_map):
            self.state_manager_visit_count_map[curr_question] = 0
        self.state_manager_visit_count_map[curr_question] += 1
        print(
            "\nVISIT COUNT for {}: {}\n".format(
                curr_question, self.state_manager_visit_count_map[curr_question]
            )
        )

    def _get_parent_state_visit_count(self):
        parent_state = self.state_manager.get_state(rollback_steps=1)
        if parent_state is None:
            return 0
        parent_question = self.state_manager.get_current_state().question
        if not (parent_question in self.state_manager_visit_count_map):
            return 0
        else:
            return self.state_manager_visit_count_map[parent_question]


class TreeOfThoughtExecutorForQuestion(TreeOfThoughtExecutorBase):
    def __init__(
        self,
        config_question,
        config_answer1,
        config_answer2,
        config_eval,
        config_subtopic,
        # ner_pipeline
    ) -> None:
        super().__init__()
        self.questions = []
        self.state_manager = QuestionStateManager()
        self.llm_agent = LLMAgent(config_question)
        self.llm1 = LLMAgent(config_answer1)
        self.llm2 = LLMAgent(config_answer2)
        self.eval_agent = LLMAgent(config_eval)
        self.topic_agent = LLMAgent(config_subtopic)
        self.parser = LLMReplyParserForQuestion()
        self.question_prompter = QuestionPrompter(
            self.llm_agent,
            self.state_manager,
            config_question.chatbot_max_context_length,
            config_question.chatbot_include_chat_history_in_query,
            PromptGenType.RuleBased,
        )
        self.answer_prompter = AnswerPrompter(
            self.llm_agent,
            self.state_manager,
            config_answer1.chatbot_max_context_length,
            config_answer1.chatbot_include_chat_history_in_query,
            PromptGenType.RuleBased,
        )
        self.eval_prompter = EvalPrompter(
            self.eval_agent,
            self.state_manager,
            config_eval.chatbot_max_context_length,
            config_eval.chatbot_include_chat_history_in_query,
            PromptGenType.RuleBased,
        )
        self.topic_prompter = EvalPrompter(
            self.topic_agent,
            self.state_manager,
            config_eval.chatbot_max_context_length,
            config_eval.chatbot_include_chat_history_in_query,
            PromptGenType.RuleBased,
        )
        # self.ner_pipeline=ner_pipeline

    def run(self, user_input, max_num_rounds):
        messages = self.question_prompter.generate_initial_prompt(user_input)
        self.state_manager.states.topic = user_input
        for i in range(max_num_rounds):
            temperature = self._get_temperature()
            max_tokens = self._get_max_tokens()
            question = ""
            em = []
            for j in range(3):
                question_json = self.llm_agent.get_reply(
                    messages, temperature, max_tokens
                )

                if "question" in question_json:
                    question = (question_json.split(":")[-1]).replace("}", "")
                else:
                    question = question_json
                Flag, em = check_similarity(
                    question,
                    self.state_manager.current_state,
                    self.questions,
                    self.state_manager.get_current_state().topic,
                )
                if Flag:
                    break
            self.questions.append(
                {
                    "question": question,
                    "embedding": em,
                    "state": copy.deepcopy(self.state_manager.current_state),
                }
            )
            answer_messages = self.answer_prompter.generate_initial_prompt(question)
            answer1 = self.llm1.get_reply(answer_messages, temperature, max_tokens * 2)
            answer2 = self.llm2.get_reply(answer_messages, temperature, max_tokens * 2)
            self._incr_state_visit_count()
            topic = self.state_manager.get_current_state().topic
            Subtopic1_message = self.eval_prompter.generate_subtopic_prompt(
                topic, question, answer1
            )
            Subtopic2_message = self.eval_prompter.generate_subtopic_prompt(
                topic, question, answer2
            )
            Eval_compare_message_1 = self.topic_prompter.generate_compare_prompt(
                question, answer1, answer2
            )
            Eval_compare_message_2 = self.topic_prompter.generate_compare_prompt(
                question, answer2, answer1
            )
            # answer1_list=split_text_uniformly(answer1)
            # Subtopic1=[]
            # for item in answer1_list:
            #     try:
            #         if len(item)==0:
            #             continue
            #         s1 = self.ner_pipeline(item)
            #         if len(s1['output'])!=0:
            #             result = sorted(s1['output'], key=lambda x: x['prob'], reverse=True)
            #             s1 = [item['span'] for item in result]
            #         else:
            #             s1 = []
            #         Subtopic1=Subtopic1+s1
            #     except:
            #         pass
            # if len(Subtopic1)==0:
            #     Subtopic1=["Empty"]
            # answer2_list=split_text_uniformly(answer2)
            # Subtopic2=[]
            # for item in answer2_list:
            #     try:
            #         if len(item)==0:
            #             continue
            #         s2 = self.ner_pipeline(item)
            #         if len(s2['output'])!=0:
            #             result = sorted(s2['output'], key=lambda x: x['prob'], reverse=True)
            #             s2 = [item['span'] for item in result]
            #         else:
            #             s2 = []
            #         Subtopic2=Subtopic2+s2
            #     except:
            #         pass
            # if len(Subtopic2)==0:
            #     Subtopic2=["Empty"]

            Subtopic1 = self.eval_agent.get_reply(
                Subtopic1_message, temperature, max_tokens / 2
            )
            Subtopic2 = self.eval_agent.get_reply(
                Subtopic2_message, temperature, max_tokens / 2
            )
            Eval_compare_1 = self.eval_agent.get_reply(
                Eval_compare_message_1, temperature, max_tokens * 2
            )
            Eval_compare_2 = self.eval_agent.get_reply(
                Eval_compare_message_2, temperature, max_tokens * 2
            )
            if i == 0:
                result = self.parser.parse_llm_reply(
                    topic,
                    question,
                    answer1,
                    answer2,
                    Subtopic1,
                    Subtopic2,
                    Eval_compare_1,
                    Eval_compare_2,
                )
            else:
                result = self.parser.parse_llm_reply_2(
                    topic,
                    question,
                    answer1,
                    answer2,
                    Subtopic1,
                    Subtopic2,
                    Eval_compare_1,
                    Eval_compare_2,
                )

            flag = self.state_manager.update_state(result)
            rollback_steps = self._get_rollback_steps(flag)
            self.conversation_history += "\nA:\nTopic:{}\nQuestion: {}\nResponse 1: {}\n Response 2: {}\n Evaluation result: {}\n".format(
                result.topic,
                result.question,
                result.answer1,
                result.answer2,
                result.question_type,
            )
            messages = self.question_prompter.generate_prompt(
                self.conversation_history, rollback_steps
            )  # FIXME
            if messages == "":
                break

        question_dict = self.state_manager.states.convert_to_dict()
        # with open(user_input+'.json', 'w') as f:
        #     json.dump(question_dict, f)
        return False, None, question_dict

    def _should_repeat(self, llm_reply):
        return "{" not in llm_reply  # FIXME: make this check more generic

    def _get_temperature(self):
        return HyperParams.DefaultTemperature

    def _get_max_tokens(self):
        return HyperParams.DefaultMaxTokens

    def _get_rollback_steps(self, flag=True):
        max_deep = HyperParams.MaxDeep
        max_rollback_steps = self.state_manager.max_rollback_steps()
        if max_rollback_steps == 0:
            rollback_steps = -1
        # elif max_rollback_steps == max_deep or flag == False:
        #     rollback_steps = 0
        else:
            rollback_steps = 0
        print("max_deep: {}".format(max_deep))
        print("max_rollback_steps: {}".format(max_rollback_steps))
        print("ROLLBACK STEPS: {}\n".format(rollback_steps))

        return rollback_steps
