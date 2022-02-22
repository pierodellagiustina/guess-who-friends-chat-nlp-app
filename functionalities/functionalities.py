import pandas as pd
import random
import config.config as c


def data_loader(num_samples):
    """Reads X number of randomly chose rows (messages) from the input file and returns them"""
    file_name = 'data/test_set.csv'
    n = sum(1 for line in open(file_name, encoding="utf-8")) - 1
    skip = sorted(random.sample(range(1, n + 1), n - num_samples))
    df = pd.read_csv(file_name, skiprows=skip, encoding="utf-8")
    return df


def get_user_preds(messages, request_form):
    """Get user predictions from POST"""
    user_preds = []

    for i in range(len(messages)):
        i += 1  # match the loop.index in jinja
        pred = request_form.get(f'answer_{i}')
        pred = str(int(pred) - 1)  # re-match to original numbering from 0
        user_preds.append(pred)

    return user_preds


def compute_user_score(user_preds, senders):
    score_user = 0

    for i, p in enumerate(user_preds):
        sender_mapper = c.SENDER_MAPPER_REV
        p = sender_mapper[int(p)]
        if p == senders[i]:
            score_user += 1

    return score_user


def split_user_preds(user_preds, num_samples):
    positions = [pos for pos, char in enumerate(user_preds) if char == '"']
    for i in chunks(positions,2):
        user_preds[i[0]:i[1]]



def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


