import os
from pull_states import pull_state_data
from batch_score_documents import score_data


def main():
    pull_state_data()
    score_data()


if __name__ == "__main__":
    main()
