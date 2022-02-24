from flask import Flask, render_template, request, url_for, redirect, session
import pandas as pd
import functionalities.functionalities as f
import config.config as c
import json

# Initialize app
app = Flask(__name__)
app.secret_key = 'gruppotelegram2'

# load the data
dataset = f.load_data()

# home page
@app.route('/', methods=['GET', 'POST'])
def index():

    # Initialize the cumulative scores
    if 'cumul_score_user' not in session:
        session['cumul_score_user'] = 0

    # Initialize attempts counter
    if 'attempts_counter' not in session:
        session['attempts_counter'] = 0

    # Read randomly chosen rows
    # todo: make num_samples dynamic
    if 'df' not in session:
        # randomly select the sample
        df = dataset.sample(c.NUM_SAMPLES)
        # turn it into json
        df = df.to_json()
        # add it to session
        session['df'] = df

    df = pd.read_json(session['df'])

    # Set up variables
    messages = df.message
    senders = df.sender
    sender_mapper = c.SENDER_MAPPER_REV
    cumul_score_user = session['cumul_score_user']
    attempts_counter = session['attempts_counter']

    if request.method == 'GET':  # request.method will tell me if it is a GET or POST request
        # Welcome page
        return render_template(
            'index.html', messages=messages, sender_mapper=sender_mapper,
            cumul_score_user=cumul_score_user, attempts_counter=attempts_counter)

    elif request.method == 'POST':
        # Get the request form
        request_form = request.form

        # If it is a request to refresh messages, do so
        if 'refresh' in request_form:
            session.pop('df')
            return redirect(url_for('index'))
        else:
            # Get user predictions from POST
            user_preds = f.get_user_preds(messages=messages, request_form=request_form)
            # Compute user score
            score_user = f.compute_user_score(user_preds, senders)
            # Update attempts counter
            session['attempts_counter'] += len(df)
            # convert to json before passing to redirect
            user_preds = json.dumps(user_preds)

            return redirect(url_for('score', score_user=score_user, user_preds=user_preds))


@app.route('/score/<score_user>/<user_preds>')
def score(score_user, user_preds):

    # Split input string and cleanse it
    user_preds = f.split_user_preds(user_preds, c.NUM_SAMPLES)

    # Remap user predictions as names
    user_preds_names = []
    for char in user_preds:
        try:
            char = int(char)
            user_preds_names.append(c.SENDER_MAPPER_REV[char])
        except:
            user_preds_names.append('err')

    # add score to the cumulative score in the session
    session['cumul_score_user'] += int(score_user)

    # read out the cumulative score
    cumul_score_user = session['cumul_score_user']

    # read out the attempts counter
    attempts_counter = session['attempts_counter']

    # read out messages and senders from the session
    df = pd.read_json(session['df'])

    # add user predictions as column to the df
    df['user_pred'] = user_preds_names

    # erase df (messages selection) from session to ensure it gets refreshed
    session.pop('df')

    # render score page
    return render_template(
        'score.html', score_user=score_user, cumul_score_user=cumul_score_user,
        attempts_counter=attempts_counter,df=df)


if __name__ == '__main__':
    app.run(debug=True)


# todo: change pictures
# todo: bring in the model estimates
