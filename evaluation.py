from inspect_ai.dataset import json_dataset
from inspect_ai import Task, task
from inspect_ai.scorer import includes
from inspect_ai.solver import generate

@task
def set_eval():
    return Task(
        dataset=json_dataset("set_game_data.jsonl"),
        plan=[
            generate()
        ],
        scorer=includes()
    )