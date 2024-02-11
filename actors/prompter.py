import json
import random
from actors.state import *
from actors.checker import *
from common.enums import PromptGenType


class PrompterBase(object):
    def __init__(self) -> None:
        pass

    def generate_initial_prompt(self) -> str:
        return ""

    def generate_prompt(self) -> str:
        return ""


class AnswerPrompter(PrompterBase):
    def __init__(
        self,
        llm_agent,
        state_manager,
        max_llm_context_length,
        include_chat_history_in_query,
        prompt_generation_type: PromptGenType,
    ) -> None:
        super().__init__()
        self.prompt_msg_buffer = ""
        self.llm_agent = llm_agent
        self.state_manager = state_manager
        self.max_llm_context_length = max_llm_context_length
        self.include_chat_history_in_query = include_chat_history_in_query
        self.prompt_generation_type = prompt_generation_type

    def generate_initial_prompt(self, user_input) -> str:
        # msg_tmpl = """Answer the following question, and your answer should be more likely to include sub-topics that can be expanded upon. Remember that you don't need to output anything else, just output your answer. You can answer in short words. Question: {}"""  # FIXME
        msg_tmpl = """Answer the following question. Remember that you don't need to output anything else, just output your answer. You can answer in short words. Question: {}"""  # FIXME
        role, msg_content = "user", msg_tmpl.format(user_input)
        msgs = self.llm_agent.compose_messages([role], [msg_content])
        return msgs


class EvalPrompter(PrompterBase):
    def __init__(
        self,
        llm_agent,
        state_manager,
        max_llm_context_length,
        include_chat_history_in_query,
        prompt_generation_type: PromptGenType,
    ) -> None:
        super().__init__()
        self.prompt_msg_buffer = ""
        self.llm_agent = llm_agent
        self.state_manager = state_manager
        self.max_llm_context_length = max_llm_context_length
        self.include_chat_history_in_query = include_chat_history_in_query
        self.prompt_generation_type = prompt_generation_type

    def generate_compare_prompt(self, question, answer1, answer2) -> str:
        msg_tmpl = """You are assessing two submitted responses to a user's query based on specific criteria. Evaluate the quality, relevance, accuracy, clarity, and any other relevant factors to determine which response is superior, or if they are equally valuable or lacking. Here is the data for your assessment:

[Query]: {0}

[Response 1]: {1}

[Response 2]: {2}

Assessment Criteria:
1. Relevance to the query: Does the response directly address the user's question or concern?
2. Accuracy of information: Are the facts or solutions provided in the response correct and reliable?
3. Clarity and comprehensibility: Is the response easy to understand, well-structured, and free of jargon or ambiguity?
4. Completeness: Does the response cover all aspects of the query or offer a comprehensive solution?
5. Additional value: Does the response provide extra insights, tips, or information that enhances the user's understanding or solves the problem more effectively?

Instructions for Assessment:
1. Identify and focus on the criteria that significantly distinguish the two responses. Disregard criteria that do not offer a clear distinction.
2. Consider any specific aspects of the query and the responses that may require additional factors for a fair comparison. Mention these factors explicitly.
3. Conclude your assessment by deciding which response is better, or if they are tied. Your decision must be based on a coherent evaluation across the mentioned criteria and any additional factors you've identified.

Please return your final decision in the following JSON format:
{{"question_type": "Response 1"/"Response 2"/"Tie"}}

Remember, the output should only contain the decision in the specified JSON format and nothing else."""  # FIXME
        role, msg_content = "user", msg_tmpl.format(question, answer1, answer2)
        msgs = self.llm_agent.compose_messages([role], [msg_content])
        return msgs

    def generate_subtopic_prompt(self, topic, question, answer) -> str:
        msg_tmpl = """
        You are asking questions and answers based on a topic you know and based on this topic. Please extract some subtopics from the answers. Here's an example:
Here is the data:
          [Input data]
          ***
          [topic]: programming languages
          ***
          [question]: Which programming languages can you write code in?
          ***
          [answer]: I know python, C++, R language, etc.
          ***
          [Output Data]
          ***
          [subtopic] : ["python","C++","R language"]

now the official question
Here is the data:
          [Input data]
          ***
          [topic]:{0}
          ***
          [question]:{1}
          ***
          [answer]:{2}
          ***
          [Output Data]
          ***
Please return your final decision in list format. Remember, you only need to output the content in the following List format, with each element as a subtopic and nothing else. Remember, you only need to output the three most important subtopics in the following List format.
[subtopic] : ["subtopic1","subtopic2","subtopic3"]
        """
        role, msg_content = "user", msg_tmpl.format(topic, question, answer)
        msgs = self.llm_agent.compose_messages([role], [msg_content])
        return msgs


class QuestionPrompter(PrompterBase):
    def __init__(
        self,
        llm_agent,
        state_manager,
        max_llm_context_length,
        include_chat_history_in_query,
        prompt_generation_type: PromptGenType,
    ) -> None:
        super().__init__()
        self.prompt_msg_buffer = ""
        self.llm_agent = llm_agent
        self.state_manager = state_manager
        self.max_llm_context_length = max_llm_context_length
        self.include_chat_history_in_query = include_chat_history_in_query
        self.prompt_generation_type = prompt_generation_type

    def generate_initial_prompt(self, user_input) -> str:
        msg_tmpl = """I want you to assume the role of the expert and ask a question that expands and reflects your understanding of {0}. Your task is to ask a question about {0}. Only by deeply understanding {0} can we answer this question correctly. Please strictly abide by the following 4 task guidelines:
        1. Your question should start with a question word, such as "what", "which", "when", "where", "how", "why", etc.
        2. The goal of the question should be to reflect the respondent's understanding of {0} and to distinguish respondents with different depths of understanding of the question.
        3. Questions should be self-contained and require no additional context or clarification.
        4. Please return your question in the JSON format below. Remember, you only need to output the content in the following format and nothing else: {{"question": your question}}"""  # FIXME
        role, msg_content = "user", msg_tmpl.format(user_input)
        msgs = self.llm_agent.compose_messages([role], [msg_content])
        return msgs

    def generate_prompt(self, conversation_history, rollback_steps):
        if self.prompt_generation_type == PromptGenType.RuleBased:
            msgs = self._generate_prompt_rule_based(
                conversation_history, rollback_steps
            )
        elif self.prompt_generation_type == PromptGenType.NeuralNetworkBased:
            msgs = self._generate_prompt_neural_network_based(
                conversation_history, rollback_steps
            )
        else:
            raise "Invalid prompt_generation_type"
        return msgs

    def _generate_prompt_rule_based(self, conversation_history, rollback_steps):
        self.checker = RuleBasedQuestionStateChecker(self.state_manager)
        rollback = self.state_manager.rollback(rollback_steps)
        rollback_state = self.state_manager.get_state(0)
        parent_state = self.state_manager.get_state(1)
        state_check_result = self.checker.check_current_state()
        solution_found = False
        if rollback == False:
            return ""
        #     rollback_msg_tmpl="""You are now back at the beginning, and you need to ask a question about {0} to better distinguish between the two models.
        #     I want you to assume the role of the expert and ask a question that expands and reflects your understanding of {0}. Your task is to ask a question about {0}. Only by deeply understanding {0} can we answer this question correctly. Please strictly abide by the following 4 task guidelines:
        # 1. Your question should start with a question word, such as "what", "which", "when", "where", "how", "why", etc.
        # 2. The goal of the question should be to reflect the respondent's understanding of {0} and to distinguish respondents with different depths of understanding of the question.
        # 3. Questions should be self-contained and require no additional context or clarification.
        # 4. Please return your question in the JSON format below. Remember, you only need to output the content in the following format and nothing else: {{"question": your question}}"""
        #     rollback_msg_content = rollback_msg_tmpl.format(rollback_state.topic)
        else:
            rollback_msg_tmpl = """I want you to assume the role of an expert and ask a question that expands on and reflects your understanding of {2} based on parent question and parent topic {0}. Your task is to ask a question about {2}. Only by deeply understanding {2} can we answer this question correctly. 
            Here is an example:
            [Input data]
            ***
            [parent topic]:programming languages
            ***
            [parent question]:Which programming languages can you write code in?
            ***
            [subtopic]:python
            ***
            [Onput data]
            ***
            [question]: What specifications should we comply with as much as possible when writing python code?

            now the official question
            Here is the data:
            [Input data]
            ***
            [parent topic]:{0}
            ***
            [parent question]:{1}
            ***
            [subtopic]:{2}
            ***
        Please strictly abide by the following 4 task guidelines:
        1. Your question should start with a question word, such as "what", "which", "when", "where", "how", "why", etc.
        2. The goal of the question should be to reflect the respondent's understanding of {2} and to distinguish respondents with different depths of understanding of the question.
        3. Questions should be self-contained and require no additional context or clarification.
        4. Please return your question in the JSON format below. Remember, you only need to output the content in the following format and nothing else: {{"question": your question}}"""
            rollback_msg_content = rollback_msg_tmpl.format(
                parent_state.topic, parent_state.question, rollback_state.topic
            )
        conversation_history += "\nQ: \n\n{}\n".format(rollback_msg_content)
        if self.include_chat_history_in_query:
            msgs = self.llm_agent.compose_messages(
                ["user"], [conversation_history[-self.max_llm_context_length :]]
            )
        else:
            msgs = self.llm_agent.compose_messages(["user"], [rollback_msg_content])
        return msgs

    def _generate_prompt_neural_network_based(self, rollback_steps):
        self.checker = RuleBasedQuestionStateChecker(self.state_manager)
        state_check_result = self.checker.check_current_state()
        return ""  # FIXME
