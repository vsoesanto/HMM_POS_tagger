'''
create_2gram_hmm.py

Vincent Soesanto
LING570
Autumn 2019
Homework 8

This script generates an bigram model of a pos-enhanced input corpus 'training_data' using the ARPA format.

Usage: cat training_data | create_2gram_hmm.sh output_hmm
'''
import sys

# command line args
input_file = sys.stdin
output_file_name = sys.argv[1]

# home development
# input_file_name = "examples/toy/toy_input"
# output_file_name = "toy_2gram_output_2"

# global variables
transition_prob = {}  # state to state
emission_prob = {}  # state to obsv
word_unigrams = {}
tag_unigrams = {}


def take_inventory(split_line):
    for i in range(len(split_line)):
        item = split_line[i]
        # by default, item is split by "/" which will capture the "/" in the word "</s>"
        if "</s>" in item:
            word = "</s>"
            tag = "EOS"
        else:
            word = split_line[i].split("/")[0]
            tag = split_line[i].split("/")[1]

        split_line[i] = (word, tag)  # modify split_line by replacing string with tuple
    # print(split_line)  # report modified split_line

    for i in range(len(split_line)):
        # state to state, e.g. BOS N
        pos_pos_ngram = ""
        for j in range(2):
            if i + j < len(split_line):
                pos_pos_ngram += split_line[i + j][1] + " "
        pos_pos_ngram = pos_pos_ngram.strip(" ")
        if len(pos_pos_ngram.split(" ")) == 2:
            # print("pos-pos ngram = " + pos_pos_ngram)
            if pos_pos_ngram not in transition_prob:
                transition_prob[pos_pos_ngram] = [0, split_line[i][1]]
            transition_prob[pos_pos_ngram] = [transition_prob[pos_pos_ngram][0] + 1, split_line[i][1]]

        # state to obsv, e.g. A cool
        pos_word_ngram = ""
        for j in range(1, -1, -1):
            pos_word_ngram += split_line[i][j] + " "
        pos_word_ngram = pos_word_ngram.strip(" ")
        if len(pos_word_ngram.split(" ")) == 2:
            # print("pos-word ngram = " + pos_word_ngram)
            if pos_word_ngram not in emission_prob:
                emission_prob[pos_word_ngram] = [0, split_line[i][1]]
            emission_prob[pos_word_ngram] = [emission_prob[pos_word_ngram][0] + 1, split_line[i][1]]

        # take word_unigram and tag_unigram counts
        word = split_line[i][0]
        tag = split_line[i][1]

        if word not in word_unigrams:
            word_unigrams[word] = 0
        word_unigrams[word] = word_unigrams[word] + 1

        if tag not in tag_unigrams:
            tag_unigrams[tag] = 0
        tag_unigrams[tag] = tag_unigrams[tag] + 1
    # print()


# DRIVER
# input from stdin
for line in input_file:
    split_line = ["<s>/BOS"] + line.strip().split(" ") + ["</s>/EOS"]
    take_inventory(split_line)

# home development
# with open(input_file_name, "r") as input_file:
#     for line in input_file:
#         split_line = ["<s>/BOS"] + line.strip("\n").split(" ") + ["</s>/EOS"]
#         # print(split_line)
#         take_inventory(split_line)

# report
with open(output_file_name, "w") as output_file:
    print("state_num=" + str(len(tag_unigrams)))
    print("sym_num=" + str(len(word_unigrams)))
    print("init_line_num=1")
    print("trans_line_num=" + str(len(transition_prob)))
    print("emiss_line_num=" + str(len(emission_prob)) + "\n")
    print("\init")

    output_file.write("state_num=" + str(len(tag_unigrams)) + "\n")
    output_file.write("sym_num=" + str(len(word_unigrams)) + "\n")
    output_file.write("init_line_num=1\n")
    output_file.write("trans_line_num=" + str(len(transition_prob)) + "\n")
    output_file.write("emiss_line_num=" + str(len(emission_prob)) + "\n\n")
    output_file.write("\init\n")

    # get init pob
    init_count = 0
    for key in transition_prob:
        if "BOS" in key:
            init_count += transition_prob[key][0]
    init_prob = init_count / tag_unigrams["BOS"]

    print("BOS " + str(float('{:.10f}'.format(init_prob))) + "\n")
    output_file.write("BOS " + str(float('{:.10f}'.format(init_prob))) + "\n\n")

    for prob_type in ['transition', 'emission']:
        print("\\" + prob_type)
        output_file.write("\\" + prob_type + "\n")
        inventory = transition_prob
        if prob_type == "emission":
            inventory = emission_prob

        # sort keys alphanumerically
        sorted_keys = sorted(inventory.keys())
        for key in sorted_keys:
            # get prob
            numerator = inventory[key][0]
            denominator = tag_unigrams[inventory[key][1]]
            print(key + " " + str(float('{:.10f}'.format(numerator/denominator))))
            output_file.write(key + " " + str(float('{:.10f}'.format(numerator / denominator))) + "\n")
        print("\n")
        output_file.write("\n")
