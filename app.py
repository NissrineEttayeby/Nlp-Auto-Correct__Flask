from flask import Flask, request, render_template
import re
import numpy as np
from collections import Counter



app = Flask(__name__)

def process(file_name):
    words = []
    with open(file_name) as f:
        file = f.read()
    file = file.lower()
    words = re.findall('\w+', file)

    return words


word_l = process('shakespeare.txt')
vocab = set(word_l)


def get_count(word_l):
    word_count_dict = {}
    word_count_dict = Counter(word_l)
    return word_count_dict


word_count_dict = get_count(word_l)


def delete_letter(word, verbose=True):
    split_l = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    delete_l = [w1 + w2[1:] for w1, w2 in split_l if w2]
    return delete_l


def switch_letter(word, verbose=False):
    split_l = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    switch_l = [a + b[1] + b[0] + b[2:] for a, b in split_l if len(b) >= 2]
    return switch_l


def replace_letter(word, verbose=False):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    split_l = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    replace_l = [a + l + (b[1:] if len(b) > 1 else '') for a, b in split_l if b for l in letters]
    replace_set = set(replace_l)
    replace_set.remove(word)
    replace_l = sorted(list(replace_set))
    return replace_l


def insert_letter(word, verbose=False):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    split_l = []
    for i in range(len(word) + 1):
        split_l.append((word[0:i], word[i:]))
    insert_l = [a + l + b for a, b in split_l for l in letters]
    return insert_l


def edit_one_letter(word, allow_switches=True):
    edit_one_set = set()
    edit_one_set.update(delete_letter(word))
    if allow_switches:
        edit_one_set.update(switch_letter(word))
    edit_one_set.update(replace_letter(word))
    edit_one_set.update(insert_letter(word))
    return edit_one_set


def edit_two_letters(word, allow_switches=True):
    edit_two_set = set()
    edit_one = edit_one_letter(word, allow_switches=allow_switches)
    for w in edit_one:
        if w:
            edit_two = edit_one_letter(w, allow_switches=allow_switches)
            edit_two_set.update(edit_two)
    return edit_two_set


def get_probs(word_count_dict):
    probs = {}
    somme = sum(word_count_dict.values())
    for key in word_count_dict.keys():
        probs[key] = word_count_dict[key] / (somme)

    return probs


probs = get_probs(word_count_dict)


def min_edit_distance(source, target, ins_cost=1, del_cost=1, rep_cost=2):
    m = len(source)
    n = len(target)
    D = np.zeros((m + 1, n + 1), dtype=int)
    for row in range(1, m + 1):  # Replace None with the proper range
        D[row, 0] = D[row - 1, 0] + del_cost

    for col in range(1, n + 1):  # Replace None with the proper range
        D[0, col] = D[0, col - 1] + ins_cost

    for row in range(1, m + 1):
        for col in range(1, n + 1):
            r_cost = rep_cost
            if source[row - 1] == target[col - 1]:
                r_cost = 0
            D[row, col] = min([D[row - 1, col] + del_cost, D[row, col - 1] + ins_cost, D[row - 1, col - 1] + r_cost])
    med = D[m, n]
    return D, med

@app.route("/corrections", methods=["POST"])
def get_corrections(n=3, verbose=False):
    word = request.form["word"]
    suggestions = list(
        (word in vocab and word) or edit_one_letter(word).intersection(vocab) or edit_two_letters(word).intersection(
            vocab))
    n_best = [i for i in list(suggestions)]

    if verbose:
        print("suggestions = ", suggestions)

    return render_template('correction.html', result=n_best[:3])


@app.route("/home")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)