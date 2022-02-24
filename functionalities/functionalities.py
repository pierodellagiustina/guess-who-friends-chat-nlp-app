import pandas as pd
import random
import config.config as c


def load_data():
    file_name = 'data/test_set.csv'
    df = pd.read_csv(file_name)
    return df


def get_user_preds(messages, request_form):
    """Get user predictions from POST and do some basic cleansing"""
    user_preds = []

    for i in range(len(messages)):
        i += 1  # match the loop.index in jinja
        pred = request_form.get(f'answer_{i}')

        try:
            pred = int(pred) - 1  # rematch original numbering
            if pred not in c.SENDER_MAPPER_REV.keys():  # if not in the list of allowed senders, return empty string
                pred = ''
        except:
            pred = ''

        user_preds.append(str(pred))

    return user_preds


def compute_user_score(user_preds, senders):
    score_user = 0

    for i, p in enumerate(user_preds):
        sender_mapper = c.SENDER_MAPPER_REV
        try:
            p = sender_mapper[int(p)]
            if p == senders[i]:
                score_user += 1
        except:
            pass

    return score_user


def split_user_preds(user_preds, num_samples):

    # The user predictions will be passed as a string with each input separated by double quotes
    # Get the position of the double quotes and then extract the substring in the middle
    positions_quotes = [pos for pos, char in enumerate(user_preds) if char == '"']
    preds_list = [user_preds[i[0]+1:i[1]] for i in chunks(positions_quotes, 2)]
    # assert len(preds_list) == num_samples

    # Convert components of preds_list to integers (they have already been checked to be in range of permitted values)
    preds_cleansed = []
    for i in range(len(preds_list)):
        try:
            intg = int(preds_list[i])
            preds_cleansed.append(intg)
        except:
            preds_cleansed.append('')

    return preds_cleansed


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


