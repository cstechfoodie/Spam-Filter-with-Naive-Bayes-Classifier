import os
import re
import math
import datetime

file_names = []  # training file names read from the give directory
ham_count = 0  # number of ham email
spam_count = 0  # number of spam email
test_file_names = []
# all tokens we found in both ham and spam emails. its length is NOT the total of (ham_tokens_count + spam_token_count_dict).
all_tokens = []
ham_tokens_count = [0]  # total tokens count in ham
ham_token_count_dict = {}  # each token with its count in ham
ham_token_prob_dict = {}  # each token with its probability in ham
spam_tokens_count = [0]  # total tokens counnt in spam
spam_token_count_dict = {}  # each token with its count in spam
spam_token_prob_dict = {}  # each token with its probability in spam

ham_email_prob = 0
spam_email_prob = 0
ham_score_dic = {}
spam_score_dic = {}
stop_word_list = []

training_set_directory = "train/"
test_set_directory = "test/"
stop_words_file = "stop-words.txt"
baseline_model_file = "baseline-model.txt"  # experiment 1
baseline_result_file = "baseline-result.txt"  # experiment 1
stop_word_model_file = "stopword-model.txt"  # experiment 2
stop_word_result_file = "stopword-result.txt"  # experiment 2
word_length_model_file = "wordlength-model.txt"  # experiment 3
word_length_result_file = "wordlength-result.txt"  # experiment 3

model_files = [baseline_model_file,
               stop_word_model_file, word_length_model_file]
result_files = [baseline_result_file,
                stop_word_result_file, word_length_result_file]

# model_files = [baseline_model_file]
# result_files = [baseline_model_file]

# model_files = [stop_word_model_file]
# result_files = [stop_word_result_file]

# model_files = [word_length_result_file]
# result_files = [word_length_result_file]


def filter_stop_words(x): return x not in stop_word_list


def filter_word_length(x): return len(x) > 2 and len(x) < 9

'''
Read all file names given the directory name, we need their names to identify whether it is a ham or spam
Here is where we save all traing files
'''


def read_file_names_in_directory(data_set_directory):
    return os.listdir(data_set_directory)


# training with a single file. need to save all info to their persistences


def training_with_one_email(file_path, tokens_count, token_count_dict,
                            token_prob_dict, filter_strategy):
    global all_tokens
    f = open(training_set_directory + file_path, "r", encoding="iso8859_2")
    lines = f.read().splitlines()
    for line in lines:
        token_list = re.split("[^a-zA-Z]", line)
        if filter_strategy == "stopword":
            # len1 = len(token_list)
            token_list = list(filter(filter_stop_words, token_list))
            # print(stop_word_list)
            # len2 = len(token_list)
            # print(str(len1-len2))
        if filter_strategy == "wordlength":
            token_list = list(filter(filter_word_length, token_list))
        for token in token_list:
            if token.strip():
                token = str(token).lower()
                if filter_strategy == "stopword" and not filter_stop_words(token):
                    continue
                else:
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


def calculate_priors():
    global ham_email_prob
    global spam_email_prob
    test_ham_count = 0
    test_spam_count = 0
    test_file_names = read_file_names_in_directory(test_set_directory)
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
    score = math.log(ham_email_prob, 10)
    f = open(test_set_directory + file_path, "r", encoding="iso8859_2")
    lines = f.read().splitlines()
    for line in lines:
        token_list = re.split("[^a-zA-Z]", line)
        #token_list = list(filter(filter_stop_words, token_list))
        #token_list = list(filter(filter_word_length, token_list))
        for token in token_list:
            if token.strip():
                token = str(token).lower()
            else:
                continue
            if token in ham_token_prob_dict:
                score = score + math.log10(ham_token_prob_dict[token])
    return score


def calculate_spam_score(file_path):
    global spam_email_prob, spam_score_dic
    score = math.log(spam_email_prob, 10)
    f = open(test_set_directory + file_path, "r", encoding="iso8859_2")
    lines = f.read().splitlines()
    for line in lines:
        token_list = re.split("[^a-zA-Z]", line)
        # token_list = list(filter(filter_stop_words, token_list))
        # token_list = list(filter(filter_word_length, token_list))
        for token in token_list:
            if token.strip():
                token = str(token).lower()
            else:
                continue
            if token in spam_token_prob_dict:
                score = score + math.log10(spam_token_prob_dict[token])
    return score


actual_ham_count = 0
actual_spam_count = 0
test_result_ham_count = 0
test_result_spam_count = 0

ham_accuracy_count = 0
spam_accuracy_count = 0

right_result_count = 0
wrong_result_count = 0


def generate_test_file(file_path):
    global right_result_count, wrong_result_count, actual_ham_count, actual_spam_count, test_result_ham_count, test_result_spam_count, ham_accuracy_count, spam_accuracy_count

    actual_ham_count = 0
    actual_spam_count = 0
    test_result_ham_count = 0
    test_result_spam_count = 0

    ham_accuracy_count = 0
    spam_accuracy_count = 0

    right_result_count = 0
    wrong_result_count = 0

    test_file_names = read_file_names_in_directory(test_set_directory)
    f = open(file_path, "w")
    line_counter = 1
    for file in sorted(test_file_names):
        if str(file).startswith("test-ham"):
            category_name = "ham"
            actual_ham_count += 1
        else:
            category_name = "spam"
            actual_spam_count += 1
        ham_score = calculate_ham_score(file)
        spam_score = calculate_spam_score(file)
        if ham_score > spam_score:
            category_test = "ham"
            test_result_ham_count += 1
        else:
            category_test = "spam"
            test_result_spam_count += 1
        if category_name == category_test:
            result = "right"
            right_result_count += 1
        else:
            result = "wrong"
            wrong_result_count += 1
        if category_test == "ham" and result == "right":
            ham_accuracy_count += 1
        if category_test == "spam" and result == "right":
            spam_accuracy_count += 1
        line = str(line_counter) + "  " + str(file) + "  " + str(category_name) + "  " + \
            str(ham_score) + "  " + str(spam_score) + "  " + \
            str(category_test) + "  " + str(result) + "\r"
        f.write(line)
        line_counter = line_counter + 1
    f.close()


def generate_report_file(filter_strategy):
    b = 1
    report_file = filter_strategy + "-report.txt"
    accuracy = right_result_count / (right_result_count + wrong_result_count)

    spam_precision = spam_accuracy_count / test_result_spam_count
    ham_precision = ham_accuracy_count / test_result_ham_count

    spam_recall = spam_accuracy_count / actual_spam_count
    ham_recall = ham_accuracy_count / actual_spam_count

    f_spam = ((b * b + 1) * spam_precision * spam_recall) / \
        (b * b * spam_precision + spam_recall)

    f_ham = ((b * b + 1) * ham_precision * ham_recall) / \
        (b * b * ham_precision + ham_recall)

    f = open(report_file, "w")
    f.write("Experiement with " + filter_strategy +
            " on " + str(datetime.datetime.now()) + "\r")
    f.write("--------------------------------------------------------------------------------------------\r")
    f.write("Model says instance is SPAM, In reality it is SPAM: " +
            str(spam_accuracy_count) + "\r")
    f.write("Model says instance is SPAM, In reality it is HAM: " +
            str(test_result_spam_count - spam_accuracy_count) + "\r")
    f.write("Model says instance is SPAM, In total: " +
            str(test_result_spam_count) + "\r")

    f.write("Model says instance is HAM, In reality it is SPAM: " +
            str(test_result_ham_count - ham_accuracy_count) + "\r")
    f.write("Model says instance is HAM, In reality it is HAM: " +
            str(ham_accuracy_count) + "\r")
    f.write("Model says instance is HAM, In total: " +
            str(test_result_ham_count) + "\r")

    f.write("Actual SPAM numbers: " + str(actual_spam_count) + "\r")
    f.write("Actual HAM numbers: " + str(actual_ham_count) + "\r")

    f.write("accracy: " + str(accuracy) + "\r")
    f.write("spam_precision: " + str(spam_precision) + "\r")
    f.write("spam_recall: " + str(spam_recall) + "\r")
    f.write("f_spam: " + str(f_spam) + "\r")
    f.write("ham_precision: " + str(ham_precision) + "\r")
    f.write("ham_recall: " + str(ham_recall) + "\r")
    f.write("f_ham: " + str(f_ham) + "\r")
    f.write("--------------------------------------------------------------------------------------------\r")
    f.close()

    f = open("comprehensive-report.txt", "a")
    f.write("\r")
    f.write("Experiement with " + filter_strategy +
            " on " + str(datetime.datetime.now()) + "\r")
    f.write("--------------------------------------------------------------------------------------------\r")
    f.write("Model says instance is SPAM, In reality it is SPAM: " +
            str(spam_accuracy_count) + "\r")
    f.write("Model says instance is SPAM, In reality it is HAM: " +
            str(test_result_spam_count - spam_accuracy_count) + "\r")
    f.write("Model says instance is SPAM, In total: " +
            str(test_result_spam_count) + "\r")

    f.write("Model says instance is HAM, In reality it is SPAM: " +
            str(test_result_ham_count - ham_accuracy_count) + "\r")
    f.write("Model says instance is HAM, In reality it is HAM: " +
            str(ham_accuracy_count) + "\r")
    f.write("Model says instance is HAM, In total: " +
            str(test_result_ham_count) + "\r")

    f.write("Actual SPAM numbers: " + str(actual_spam_count) + "\r")
    f.write("Actual HAM numbers: " + str(actual_ham_count) + "\r")

    f.write("accracy: " + str(accuracy) + "\r")
    f.write("spam_precision: " + str(spam_precision) + "\r")
    f.write("spam_recall: " + str(spam_recall) + "\r")
    f.write("f_spam: " + str(f_spam) + "\r")
    f.write("ham_precision: " + str(ham_precision) + "\r")
    f.write("ham_recall: " + str(ham_recall) + "\r")
    f.write("f_ham: " + str(f_ham) + "\r")
    f.write("--------------------------------------------------------------------------------------------\r")
    f.close()


def read_stop_word_from_file(file_name):
    f = open(file_name, "r", encoding="iso8859_2")
    lines = f.read().splitlines()
    f.close()
    return lines


index = 0
stop_word_list = read_stop_word_from_file(stop_words_file)
print(stop_word_list)
length = len(model_files)
print(model_files)
while(index < length):
    filter_strategy = model_files[index].split("-")[0]
    file_names_for_training = read_file_names_in_directory(
        training_set_directory)
    for file in file_names_for_training:
        if str(file).startswith("train-ham"):
            print("Currently Training with file: " + file +
                  " -- strategy key [" + filter_strategy + "]")
            ham_count = ham_count + 1
            training_with_one_email(file, ham_tokens_count, ham_token_count_dict,
                                    ham_token_prob_dict, filter_strategy)
        else:
            print("Currently Training with file: " + file +
                  " -- strategy key [" + filter_strategy + "]")
            spam_count = spam_count + 1
            training_with_one_email(file, spam_tokens_count, spam_token_count_dict,
                                    spam_token_prob_dict, filter_strategy)
    calculate_probabilities()
    generate_model_file(model_files[index])
    calculate_priors()
    generate_test_file(result_files[index])
    generate_report_file(filter_strategy)
    index += 1

    file_names = []  # training file names read from the give directory
    ham_count = 0  # number of ham email
    spam_count = 0  # number of spam email
    test_file_names = []
    # all tokens we found in both ham and spam emails. its length is NOT the total of (ham_tokens_count + spam_token_count_dict).
    all_tokens = []
    ham_tokens_count = [0]  # total tokens count in ham
    ham_token_count_dict = {}  # each token with its count in ham
    ham_token_prob_dict = {}  # each token with its probability in ham
    spam_tokens_count = [0]  # total tokens counnt in spam
    spam_token_count_dict = {}  # each token with its count in spam
    spam_token_prob_dict = {}  # each token with its probability in spam

    ham_email_prob = 0
    spam_email_prob = 0
    ham_score_dic = {}
    spam_score_dic = {}
