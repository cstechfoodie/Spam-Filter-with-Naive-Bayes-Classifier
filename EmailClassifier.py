import os

file_names = []  # training file names read from the give directory
ham_count = 0  # number of ham email
spam_count = 0  # number of spam email

ham_words_count = 0  # total words count in ham
ham_word_count_dict = {}  # each word with its count in ham
spam_words_count = 0  # total words ounnt in spam
spam_word_count_dict = {}  # each word with its count in spam

training_set_directory = "train/"
test_set_directory = "test/"


def read_file_names_in_directory():
    global file_names, training_set_directory
    file_names = os.listdir(training_set_directory)


def training_with_one_email(file_path):
    return 1
