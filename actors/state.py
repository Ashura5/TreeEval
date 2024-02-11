import json
import actors.checker as checker
from common.hyperparams import HyperParams


class StateManagerBase(object):
    def __init__(self) -> None:
        pass

    def update_state(self, state_update_instructions) -> bool:
        pass

    def get_current_state(self) -> object:
        return None

    def get_state(self, rollback_steps) -> object:
        return None

    def rollback(self, rollback_steps) -> object:
        pass


class QuestionStateManager(StateManagerBase):
    def __init__(self, topic="") -> None:
        super().__init__()
        self.states = checker.QuestionStateCheckResults(
            topic=topic,
            question="",
            answer1="",
            answer2="",
            question_type="",
            lchild_topic=[],
            rchild_topic=[],
            topic_from="init",
        )
        self.current_state = []

    def update_state(self, question_result) -> bool:
        state = self.get_current_state()
        state.question = question_result.question
        state.answer1 = question_result.answer1
        state.answer2 = question_result.answer2
        state.question_type = question_result.question_type
        state.lchild_topic = question_result.lchild_topic
        state.rchild_topic = question_result.rchild_topic
        for l_topic in question_result.lchild_topic:
            if l_topic in question_result.rchild_topic:
                state.add_child(
                    checker.QuestionStateCheckResults(
                        topic=l_topic,
                        question="",
                        answer1="",
                        answer2="",
                        question_type="",
                        lchild_topic=[],
                        rchild_topic=[],
                        topic_from="both",
                    )
                )
            else:
                state.add_child(
                    checker.QuestionStateCheckResults(
                        topic=l_topic,
                        question="",
                        answer1="",
                        answer2="",
                        question_type="",
                        lchild_topic=[],
                        rchild_topic=[],
                        topic_from="lchild",
                    )
                )
        for r_topic in question_result.rchild_topic:
            if r_topic not in question_result.lchild_topic:
                state.add_child(
                    checker.QuestionStateCheckResults(
                        topic=r_topic,
                        question="",
                        answer1="",
                        answer2="",
                        question_type="",
                        lchild_topic=[],
                        rchild_topic=[],
                        topic_from="rchild",
                    )
                )
        if len(state.children) == 0:
            return False
        # self.current_state.append(0)
        return True

    def get_current_state(self) -> object:
        res = self.states
        for i in self.current_state:
            res = res.children[i]
        return res

    def is_at_initial_state(self) -> bool:
        return len(self.current_state) == 0

    def get_initial_state(self) -> object:
        return self.states

    def get_state(self, rollback_steps) -> object:
        if len(self.current_state) < rollback_steps:
            return None
        if rollback_steps == 0:
            return self.get_current_state()
        res = self.states
        for i in self.current_state[:-rollback_steps]:
            res = res.children[i]
        return res

    def rollback(self, rollback_steps) -> bool:
        if len(self.current_state) <= rollback_steps:
            self.current_state = []
            return False
        if len(self.current_state) == 0:
            self.current_state.append(0)
            return True
        print("START STATE ROLLBACK, current depth: {}".format(len(self.current_state)))
        if rollback_steps > 0:
            try:
                self.current_state = self.current_state[:-rollback_steps]
                while self.get_current_state().question != "":
                    self.current_state[-1] = self.current_state[-1] + 1
            except:
                return self.rollback(1)
        elif rollback_steps == 0:
            try:
                self.current_state[-1] = self.current_state[-1] + 1
                stat = self.states
                for s in self.current_state:
                    print("topic:", stat.children[s].topic)
                    print("question:", stat.children[s].question)
                    stat = stat.children[s]
                print(
                    "STATE ROLLBACK DONE,  current depth: {}\n".format(
                        len(self.current_state)
                    )
                )
                return True
            except:
                max_deep = HyperParams.MaxDeep
                if len(self.current_state) > max_deep:
                    return self.rollback(1)
                p = self.get_state(1)
                for stat in p.children:
                    left = 0
                    right = 0
                    tie = 0
                    if (
                        stat.topic_from == "lchild"
                        and stat.question_type == "Response 1"
                    ):
                        left = left + 1
                    if (
                        stat.topic_from == "lchild"
                        and stat.question_type == "Response 2"
                    ):
                        right = right + 2
                    if (
                        stat.topic_from == "rchild"
                        and stat.question_type == "Response 1"
                    ):
                        left = left + 2
                    if (
                        stat.topic_from == "rchild"
                        and stat.question_type == "Response 2"
                    ):
                        right = right + 1
                    if stat.topic_from == "both" and stat.question_type == "Response 1":
                        left = left + 4
                    if stat.topic_from == "both" and stat.question_type == "Response 2":
                        right = right + 4
                    if stat.question_type == "Tie":
                        tie = tie + 1
                        if stat.topic_from == "both":
                            tie = tie + 1
                if left >= right + tie:
                    return self.rollback(1)
                if right >= left + tie:
                    return self.rollback(1)
                self.current_state[-1] = 0
                return self.rollback(-1)
        else:
            try:
                while self.get_current_state().question_type != "Tie":
                    self.current_state[-1] = self.current_state[-1] + 1
                self.current_state.append(0)
                return True
            except:
                return self.rollback(1)

    # def rollback(self, rollback_steps) -> bool:
    #     if len(self.current_state) < rollback_steps:
    #         self.current_state = []
    #         return False
    #     print("START STATE ROLLBACK, current depth: {}".format(len(self.current_state)))
    #     if rollback_steps == -1:
    #         state = self.get_current_state()
    #         if len(state.children) > 0:
    #             self.current_state.append(0)
    #             return True
    #         else:
    #             return self.rollback(0)
    #     try:
    #         if rollback_steps > 0:
    #             self.current_state = self.current_state[:-rollback_steps]
    #         self.current_state[-1] = self.current_state[-1] + 1
    #         stat = self.states
    #         for s in self.current_state:
    #             print("topic:", stat.children[s].topic)
    #             print("question:", stat.children[s].question)
    #             stat = stat.children[s]
    #         print(
    #             "STATE ROLLBACK DONE,  current depth: {}\n".format(
    #                 len(self.current_state)
    #             )
    #         )
    #         return True
    #     except:
    #         print(
    #             "STATE ROLLBACK FAILED,  current depth: {}\n".format(
    #                 len(self.current_state)
    #             )
    #         )
    #         return self.rollback(1)

    def max_rollback_steps(self) -> int:
        return len(self.current_state)


# M=QuestionStateManager("shopping")
# st=checker.QuestionStateCheckResults(topic="shopping",question="",answer1="",answer2="",question_type="",lchild_topic=["1","2","3"],rchild_topic=["4","5","6"],topic_from="init")
# M.update_state(st)
# M.get_current_state().question
# M.get_initial_state().question
# M.max_rollback_steps()
# M.get_state(1).question
# M.rollback(1)
# M.get_current_state().question
# M.update_state(st)
