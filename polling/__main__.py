from sys import argv

from .suggest_workshop import SuggestWorkshop

ALL_FUNCTIONS = dict([
    ("SuggestWorkshop", SuggestWorkshop)
])

if __name__ == "__main__":
    if len(argv) != 2 or argv[1] not in ALL_FUNCTIONS:
        print("Error: No valid function provided.")
        print()
        print("All functions:")
        print(" ", "\n  ".join(ALL_FUNCTIONS.keys()))
        exit(1)

    ALL_FUNCTIONS[argv[1]]()