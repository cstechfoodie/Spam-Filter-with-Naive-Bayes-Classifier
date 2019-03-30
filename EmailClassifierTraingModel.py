import os
import re

file_names = []  # training file names read from the give directory
ham_count = 0  # number of ham email
spam_count = 0  # number of spam email

all_tokens = []
ham_tokens_count = 0  # total tokens count in ham
ham_token_count_dict = {}  # each token with its count in ham
ham_token_prob_dict = {}  # each token with its probability in ham
spam_tokens_count = 0  # total tokens counnt in spam
spam_token_count_dict = {}  # each token with its count in spam
spam_token_prob_dict = {}  # each token with its probability in spam

training_set_directory = "train/"
test_set_directory = "test/"
generated_model_file = "model.txt"


def read_file_names_in_directory():
    training_set_directory
    return os.listdir(training_set_directory)


def training_with_one_email(file_path, tokens_count, token_count_dict, token_prob_dict):
    global all_tokens
    f = open("file_path", "r")
    lines = f.read().splitlines()
    for line in lines:
        token_list = re.split("^([a-zA-Z]+)$", line.lower)
        tokens_count = len(token_list) + tokens_count
        for token in token_list:
            if token in token_list:
                token_count_dict[token] = token_count_dict[token] + 1
            else:
                token_count_dict[token] = 1
            if token not in all_tokens:
                all_tokens = all_tokens.append(token)


def calculate_probabilities():
    global ham_token_count_dict, spam_token_count_dict
    for token, count in ham_token_count_dict:
        ham_token_prob_dict[token] = (
            count + 0.5) / (ham_tokens_count + 0.5 * len(ham_token_count_dict.keys))
    for token, count in spam_token_count_dict:
        spam_token_prob_dict[token] = (
            count + 0.5) / (spam_tokens_count + 0.5 * len(spam_token_count_dict.keys))


def generate_model_file(file_name):
    global all_tokens
    f = open(file_name, "w")
    line_counter = 1
    for token in sorted(all_tokens):
        if token in ham_token_count_dict:
            token_count_in_ham = str(ham_token_count_dict[token])
            toekn_prob_in_ham = str(ham_token_prob_dict[token])
        else:
            token_count_in_ham = str(0)
            toekn_prob_in_ham = str(0)
        if token in spam_token_count_dict:
            token_count_in_spam = str(spam_token_count_dict[token])
            toekn_prob_in_spam = str(spam_token_prob_dict[token])
        else:
            token_count_in_spam = str(0)
            toekn_prob_in_spam = str(0)
        line = str(line_counter) + "  " + str(token) + "  " + token_count_in_ham + "  " + \
            toekn_prob_in_ham + "  " + token_count_in_spam + "  " + toekn_prob_in_spam + "\r"
        f.write(line)
        line_counter = line_counter + 1
    f.close()


# script starts from here
file_names = read_file_names_in_directory()
for file in file_names:
    if str(file).startswith("training-ham"):
        ham_count = ham_count + 1
        training_with_one_email(file, ham_tokens_count,
                                ham_token_count_dict, ham_token_prob_dict)
    else:
        spam_count = spam_count + 1
        training_with_one_email(file, spam_tokens_count,
                                spam_token_count_dict, spam_token_prob_dict)
calculate_probabilities()
generate_model_file(generate_model_file)
