from sys import argv

from machine_learning.process_pending_rating import ProcessPendingRating
from machine_learning.update_models import UpdateModels

ALL_FUNCTIONS = dict([
    ("UpdateModels", UpdateModels),
    ("ProcessPendingRating", ProcessPendingRating),
])


if __name__ == "__main__":
    if len(argv) != 2 or argv[1] not in ALL_FUNCTIONS:
        print("Error: No valid function provided.")
        print()
        print("All functions:")
        print(" ", "\n  ".join(ALL_FUNCTIONS.keys()))
        exit(1)

    ALL_FUNCTIONS[argv[1]]()
