import json
from random import choice as randchoice
from random import shuffle as randshuffle
from icecream import ic
from flask import redirect

from miscellaneous import hasher
from firebase_functions import get_team_details, update_team_details


def answerify(given_answer: str) -> str:
    return given_answer.strip().replace(" ", "").casefold()


def get_questions() -> list:
    with open("./questions.json", "r") as f:
        question_list = json.load(f)
    return question_list


# ic(get_questions())

TOTAL_Q = len(get_questions())


def perhaps_completed(regno: str, current_ques: int):
    current_ques = int(current_ques)
    # ic(    current_ques,        len((str_sequence_to_int_list(get_team_details(regno, "sequence")))),        TOTAL_Q,)
    if current_ques > len(
        str_sequence_to_int_list(get_team_details(regno, "sequence"))
    ):
        return True
    if current_ques > TOTAL_Q:
        return True
    return False


class Question:
    def __init__(self, question_num_in_list: int):
        print(len(get_questions()), question_num_in_list)
        question = get_questions()[int(question_num_in_list) - 1]
        self.type = question["type"]
        self.text = question["text"]
        self.answer = answerify(question["ans"])
        self.hint = question["hint"]
        self.smol_ans = hasher(self.answer)
        self.difficulty = question["difficulty"]
        self.no = question["no"]
        self.location = question["location"]
        self.key = question["key"]
        print(question)

    def check_answer(self, given_answer: str) -> bool:
        if answerify(given_answer) == self.answer:
            return True
        return False


def get_answer_for_a_question(question_number: int | str = 1) -> str:
    q = Question(question_number)
    return q.answer


def hint_used(regno: str):
    regno = regno.casefold()
    get_personal_current_question(regno)
    update_team_details(regno, "hint_used", True)
    chu = str_sequence_to_int_list(get_team_details(regno, "hints_used"))
    chu.append(int(get_team_details(regno, "current_question")))
    update_team_details(
        regno,
        "hints_used",
        str(chu),
    )


def get_personal_current_question(regno: str):
    current_question = int(get_team_details(regno, "current_question"))
    if perhaps_completed(regno, current_question):
        return redirect("/completed")
    sequence = get_team_details(regno, "sequence")
    player_sequence = str_sequence_to_int_list(sequence)
    # ic(player_sequence, current_question)
    return Question(player_sequence[current_question - 1])


# -----------------------------------------------------------------


def str_sequence_to_int_list(sequence: str) -> list[int]:
    if sequence:
        to_return = sequence.strip("[").strip("]").split(",")
        for i in range(len(to_return)):
            to_return[i] = int(to_return[i].strip().strip("'"))
        return to_return


def get_specific_difficulty_questions(question_dict: dict, difficuty: str) -> list[int]:
    to_return = [
        i + 1
        for i in range(len(question_dict))
        if question_dict[i]["difficulty"].casefold() == difficuty.casefold()
    ]
    return to_return if to_return else []


def generate_sequence_for_a_team() -> list[int]:
    """Generates a sequence of questions for each team."""
    question_dict = get_questions()

    start_questions = get_specific_difficulty_questions(question_dict, "start")

    easy_questions = get_specific_difficulty_questions(question_dict, "easy")
    medium_questions = get_specific_difficulty_questions(question_dict, "medium")
    hard_questions = get_specific_difficulty_questions(question_dict, "hard")
    ctfe_questions = get_specific_difficulty_questions(question_dict, "ctfe")
    ctfm_questions = get_specific_difficulty_questions(question_dict, "ctfm")

    # print(easy_questions, medium_questions, hard_questions)
    ic(easy_questions, medium_questions, hard_questions, ctfe_questions, ctfm_questions)
    sequence = []
    if start_questions:
        randshuffle(start_questions)
        sequence += start_questions[:1]
    if easy_questions:
        randshuffle(easy_questions)
        sequence += easy_questions[:2]
    if medium_questions:
        randshuffle(medium_questions)
        sequence += medium_questions[:2]
    if hard_questions:
        randshuffle(hard_questions)
        sequence += hard_questions[:1]
    if ctfe_questions:
        randshuffle(ctfe_questions)
        sequence += ctfe_questions[:2]
    if ctfm_questions:
        randshuffle(ctfm_questions)
        sequence += ctfm_questions[:1]
    return sequence


# -----------------------------------------------------------------
