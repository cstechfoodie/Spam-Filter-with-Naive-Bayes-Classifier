import os
import re

file_names = []  # training file names read from the give directory
ham_count = 0  # number of ham email
spam_count = 0  # number of spam email
prior_ham = 0
prior_spam = 0

# all tokens we found in both ham and spam emails. its length is NOT the total of (ham_tokens_count + spam_token_count_dict).
all_tokens = []
ham_tokens_count = [0]  # total tokens count in ham
ham_token_count_dict = {}  # each token with its count in ham
ham_token_prob_dict = {}  # each token with its probability in ham
spam_tokens_count = [0]  # total tokens counnt in spam
spam_token_count_dict = {}  # each token with its count in spam
spam_token_prob_dict = {}  # each token with its probability in spam

training_set_directory = "train/"
# training_set_directory = "simple-train-set-for-develop/"
test_set_directory = "test/"
generated_model_file = "model.txt"
baseline_result = "baseline-result.txt"  # Experiment 1
stopword_result = "stopword-result.txt"  # Experiment 2
wordlength_result = "wordlength_result.txt"  # Experiment 3
'''
Read all file names given the directory name, we need their names to identify whether it is a ham or spam
Here is where we save all traing files
'''


def read_file_names_in_directory(data_set_directory):
    return os.listdir(data_set_directory)


# training with a single file. need to save all info to their persistences


def training_with_one_email(file_path, tokens_count, token_count_dict,
                            token_prob_dict):
    global all_tokens
    f = open(training_set_directory + file_path, "r", encoding="iso8859_2")
    lines = f.read().splitlines()
    for line in lines:
        token_list = re.split("[^a-zA-Z]", line)
        for token in token_list:
            if token.strip():
                token = str(token).lower()
                tokens_count[0] = tokens_count[0] + 1
            else:
                continue
            if token in token_count_dict:
                token_count_dict[token] = token_count_dict[token] + 1
            else:
                token_count_dict[token] = 1
            if token not in all_tokens:
                all_tokens.append(token)


# smooth with 0.5 - assume each token will at least show 0.5 time


def calculate_probabilities():
    global ham_token_count_dict, spam_token_count_dict
    smooth_constant = 0.5
    vocabulary_len = len(all_tokens)
    for token in all_tokens:
        if token in ham_token_count_dict.keys():
            ham_token_prob_dict[token] = (
                ham_token_count_dict[token] + smooth_constant) / (
                    ham_tokens_count[0] + smooth_constant * vocabulary_len)
        else:
            ham_token_prob_dict[token] = smooth_constant / \
                (ham_tokens_count[0] + smooth_constant * vocabulary_len)
        if token in spam_token_count_dict.keys():
            spam_token_prob_dict[token] = (
                spam_token_count_dict[token] + smooth_constant) / (
                    spam_tokens_count[0] + smooth_constant * vocabulary_len)
        else:
            spam_token_prob_dict[token] = smooth_constant / \
                (spam_tokens_count[0] + smooth_constant * vocabulary_len)


def generate_model_file(file_name):
    global all_tokens
    f = open(file_name, "w")
    line_counter = 1
    for token in sorted(all_tokens):
        if token in ham_token_count_dict:
            token_count_in_ham = int(ham_token_count_dict[token])
        else:
            token_count_in_ham = int(0)
        if token in spam_token_count_dict:
            token_count_in_spam = int(spam_token_count_dict[token])
        else:
            token_count_in_spam = int(0)
        toekn_prob_in_ham = float(ham_token_prob_dict[token])
        toekn_prob_in_spam = float(spam_token_prob_dict[token])

        line = '%d  %s  %d %.7f  %d  %.7f\n' % (
            line_counter, token, token_count_in_ham, toekn_prob_in_ham,
            token_count_in_spam, toekn_prob_in_spam)
        f.write(line)
        line_counter = line_counter + 1
    f.close()


# script starts from here
file_names_for_training = read_file_names_in_directory(training_set_directory)
for file in file_names_for_training:
    if str(file).startswith("train-ham"):
        print("Currently Training with file: " + file)
        ham_count = ham_count + 1
        training_with_one_email(file, ham_tokens_count, ham_token_count_dict,
                                ham_token_prob_dict)
    else:
        print("Currently Training with file: " + file)
        spam_count = spam_count + 1
        training_with_one_email(file, spam_tokens_count, spam_token_count_dict,
                                spam_token_prob_dict)
calculate_probabilities()
generate_model_file(generated_model_file)

prior_ham = ham_count / (ham_count + spam_count)
prior_spam = spam_count / (ham_count + spam_count)
