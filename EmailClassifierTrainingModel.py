import os
import re
import math

file_names = []  # training file names read from the give directory
ham_count = 0  # number of ham email
spam_count = 0  # number of spam email

test_file_names = []


# all tokens we found in both ham and spam emails. its length is NOT the total of (ham_tokens_count + spam_token_count_dict).
all_tokens = []
ham_tokens_count = 0  # total tokens count in ham
ham_token_count_dict = {}  # each token with its count in ham
ham_token_prob_dict = {}  # each token with its probability in ham
spam_tokens_count = 0  # total tokens counnt in spam
spam_token_count_dict = {}  # each token with its count in spam
spam_token_prob_dict = {}  # each token with its probability in spam

ham_email_prob = 0
spam_email_prob = 0
ham_score_dic = {}
spam_score_dic = {}

training_set_directory = "simple-train-set-for-develop/"
test_set_directory = "test/"
generated_model_file = "model.txt"


'''
Read all file names given the directory name, we need their names to identify whether it is a ham or spam
Here is where we save all traing files
'''


def read_file_names_in_directory():
    training_set_directory
    return os.listdir(training_set_directory)

# training with a single file. need to save all info to their persistences


def training_with_one_email(file_path, tokens_count, token_count_dict, token_prob_dict):
    global all_tokens
    f = open(training_set_directory + file_path,
             "r", encoding="iso8859_2")
    lines = f.read().splitlines()
    for line in lines:
        token_list = re.split("[^a-zA-Z]", line)
        tokens_count = len(token_list) + tokens_count
        for token in token_list:
            if token.strip():
                token = str(token).lower()
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
    vocabulary_len = len(all_tokens)
    for token in all_tokens:
        if token in ham_token_count_dict.keys():
            ham_token_prob_dict[token] = (
                ham_token_count_dict[token] + 0.5) / (ham_tokens_count + 0.5 * vocabulary_len)
        else:
            ham_token_prob_dict[token] = 0.5 / \
                (ham_tokens_count + 0.5 * vocabulary_len)
        if token in spam_token_count_dict.keys():
            spam_token_prob_dict[token] = (
                spam_token_count_dict[token] + 0.5) / (spam_tokens_count + 0.5 * vocabulary_len)
        else:
            spam_token_prob_dict[token] = 0.5 / \
                (spam_tokens_count + 0.5 * vocabulary_len)


def generate_model_file(file_name):
    global all_tokens
    f = open(file_name, "w")
    line_counter = 1
    for token in sorted(all_tokens):
        if token in ham_token_count_dict:
            token_count_in_ham = str(ham_token_count_dict[token])
        else:
            token_count_in_ham = str(0)
        if token in spam_token_count_dict:
            token_count_in_spam = str(spam_token_count_dict[token])
        else:
            token_count_in_spam = str(0)
        toekn_prob_in_ham = str(ham_token_prob_dict[token])
        toekn_prob_in_spam = str(spam_token_prob_dict[token])
        line = str(line_counter) + "  " + str(token) + "  " + token_count_in_ham + "  " + \
            toekn_prob_in_ham + "  " + token_count_in_spam + "  " + toekn_prob_in_spam + "\r"
        f.write(line)
        line_counter = line_counter + 1
    f.close()


def read_files_in_directory(file_path):
    return os.listdir(file_path)


def count_test_category_prob():
    global ham_email_prob
    global spam_email_prob
    test_ham_count = 0
    test_spam_count = 0
    test_file_names = read_files_in_directory(test_set_directory)
    for file in test_file_names:
        if str(file).startswith("test-ham"):
            print("Currently testing with file: " + file)
            test_ham_count = test_ham_count + 1
        else:
            print("Currently testing with file: " + file)
            test_spam_count = test_spam_count + 1
    ham_email_prob = test_ham_count / (test_ham_count + test_spam_count)
    spam_email_prob = test_spam_count / (test_ham_count + test_spam_count)


def calculate_ham_score(file_path):
    global ham_email_prob
    global ham_score_dic
    score = math.log(ham_email_prob, 10)
    f = open(test_set_directory + file_path, "r", encoding="iso8859_2")
    lines = f.read().splitlines()
    for line in lines:
        token_list = re.split("[^a-zA-Z]", line)
        for token in token_list:
            if token.strip():
                token = str(token).lower()
            else:
                continue
            if token in ham_token_prob_dict:
                score = score + math.log10(ham_token_prob_dict[token])
    return score


def calculate_spam_score(file_path):
    global spam_email_prob
    global spam_score_dic
    score = math.log(spam_email_prob, 10)
    f = open(test_set_directory + file_path, "r", encoding="iso8859_2")
    lines = f.read().splitlines()
    for line in lines:
        token_list = re.split("[^a-zA-Z]", line)
        for token in token_list:
            if token.strip():
                token = str(token).lower()
            else:
                continue
            if token in spam_token_prob_dict:
                score = score + math.log10(spam_token_prob_dict[token])
    return score


# script starts from here
file_names = read_file_names_in_directory()
for file in file_names:
    if str(file).startswith("train-ham"):
        print("Currently Training with file: " + file)
        ham_count = ham_count + 1
        training_with_one_email(file, ham_tokens_count,
                                ham_token_count_dict, ham_token_prob_dict)
    else:
        print("Currently Training with file: " + file)
        spam_count = spam_count + 1
        training_with_one_email(file, spam_tokens_count,
                                spam_token_count_dict, spam_token_prob_dict)


calculate_probabilities()
# generate_model_file(generated_model_file)

count_test_category_prob()


def generate_test_file():
    test_file_names = read_files_in_directory(test_set_directory)
    f = open("baseline-result.txt", "w")
    line_counter = 1
    for file in sorted(test_file_names):
        if str(file).startswith("test-ham"):
            category_name = "ham"
        else:
            category_name = "spam"
        ham_score = calculate_ham_score(file)
        spam_score = calculate_spam_score(file)
        if ham_score > spam_score:
            category_test = "ham"
        else:
            category_test = "spam"
        if category_name == category_test:
            result = "right"
        else:
            result = "wrong"

        line = str(line_counter) + "  " + str(file) + "  " + str(category_name) + "  " + \
               str(ham_score) + "  " + str(spam_score) + "  " + str(category_test) + "  " + str(result) + "\r"
        f.write(line)
        line_counter = line_counter + 1
    f.close()


generate_test_file()





