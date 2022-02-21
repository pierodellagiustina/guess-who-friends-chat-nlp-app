from flask import Flask, render_template, request, url_for, redirect, session
import pandas as pd
import joblib
import functionalities.functionalities as f
import config.config as c

# Initialize app
app = Flask(__name__)
app.secret_key = 'gruppotelegram'

# # Set up the global scores
# global cumul_score_user
# cumul_score_user = 0
#
# global cumul_score_nn
# cumul_score_nn = 0


# Start the app
@app.route('/', methods=['GET', 'POST'])
def index():

    # Initialize the cumulative scores
    if 'cumul_score_user' not in session:
        session['cumul_score_user'] = 0

    # Read randomly chosen rows
    # todo: make num_samples dynamic
    if 'df' not in session:
        # randomly select the sample
        df = f.data_loader(c.NUM_SAMPLES)
        # turn it into json
        df = df.to_json()
        # add it to session
        session['df'] = df

    df = pd.read_json(session['df'])

    messages = df.message
    senders = df.sender
    sender_mapper = c.SENDER_MAPPER_REV

    print(df)


    if request.method == 'GET':  # request.method will tell me if it is a GET or POST request
        # Welcome page
        return render_template('index.html', messages=messages, sender_mapper=sender_mapper)

    elif request.method == 'POST':
        # Get user predictions from POST
        user_preds = f.get_user_preds(messages=messages, request_form=request.form)
        # Compute user score
        score_user = f.compute_user_score(user_preds, senders)

        return redirect(url_for('score', score_user=score_user))


@app.route('/second_page')
def second_page():
    return render_template('second_page.html')


@app.route('/score')
def score():
    # get the user score in the last round
    score_user = request.args['score_user']
    # add it to the cumulative score in the session
    session['cumul_score_user'] += int(score_user)
    # read out the cumulative score
    cumul_score_user = session['cumul_score_user']
    # erase messages selection from session to ensure it gets refreshed
    session.pop('df')

    return render_template(
        'score.html', score_user=score_user, cumul_score_user=cumul_score_user)


if __name__ == '__main__':
    # app.config['df'] = df
    app.run(debug=True)
