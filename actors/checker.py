import json
import copy
import common.consts as consts


class StateCheckerBase(object):
    def __init__(self, state_manager) -> None:
        self.state_manager = state_manager

    def check_current_state(self):
        return None


class QuestionStateCheckResults:
    def __init__(
        self,
        topic,
        question,
        answer1,
        answer2,
        question_type,
        lchild_topic,
        rchild_topic,
        topic_from,
        is_valid=True,
    ) -> None:
        self.topic = topic
        self.topic_from = topic_from
        self.question = question
        self.answer1 = answer1
        self.answer2 = answer2
        # self.question_difficulty = question_difficulty
        self.question_type = question_type
        self.lchild_topic = lchild_topic
        self.rchild_topic = rchild_topic
        self.child_topic = self.lchild_topic + self.rchild_topic
        self.children = []
        self.is_valid = is_valid

    def add_child(self, child):
        self.children.append(child)

    def convert_to_dict(self):
        return {
            "topic": self.topic,
            "topic_from": self.topic_from,
            "question": self.question,
            "answer1": self.answer1,
            "answer2": self.answer2,
            "lchild_topic": self.lchild_topic,
            "rchild_topic": self.rchild_topic,
            # "question_difficulty": self.question_difficulty,
            "question_type": self.question_type,
            "children": [child.convert_to_dict() for child in self.children],
            "is_valid": self.is_valid,
        }


class RuleBasedQuestionStateChecker(StateCheckerBase):
    def __init__(self, state_manager) -> None:
        super().__init__(state_manager)

    def check_current_state(self):
        current_question = self.state_manager.get_current_state()
        return current_question

    def check_question(current_question):
        # result = QuestionStateCheckResults()

        return current_question

    def _has_duplicates(vec):
        if len(vec) <= 1:
            return False
        v = copy.deepcopy(vec)
        v = sorted(v)
        for i in range(len(v) - 1):
            if (not (str(v[i]) == "*")) and v[i] == v[i + 1]:
                return True, v[i]
        return False, None


class LLMBasedSudokuStateChecker(StateCheckerBase):
    def __init__(self, state_manager) -> None:
        super().__init__(state_manager)

    def check_current_state(self):
        return None
