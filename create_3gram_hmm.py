'''
create_3gram_hmm.py


Vincent Soesanto
CSE 415
Autumn 2019

This script generates an trigram model of a pos-enhanced input corpus 'training_data' using the ARPA format.
Interpolation is used as the smoothing technique for this model.

Usage: cat training_data | create_3gram_hmm.sh output_hmm l1 l2 l3 unk_prob_file
'''
import sys
import math

# command line args
input_file = sys.stdin
output_file_name = sys.argv[1]
l1 = float(sys.argv[2])
l2 = float(sys.argv[3])
l3 = float(sys.argv[4])
unk_prob_file_name = sys.argv[5]

# for home development
# input_file_name = "examples/wsj_sec0.word_pos"
# # input_file_name = "examples/toy/toy_input"
# output_file_name = "wsj_hmm_3g"
# # output_file_name = "toy_hmm_3g"
# l1 = 0.2
# l2 = 0.3
# l3 = 0.5
# unk_prob_file_name = "examples/unk_prob_sec22"
# # unk_prob_file_name = "examples/toy/toy_unk"

# global variables
emission_prob = {}
word_bigrams = {}
word_unigrams = {"<unk>": 0}
tag_bigrams = {}
tag_trigrams = {}
tag_unigrams = {}
tag_set = set()
unk_prob = {}
total_tag_types = 0

# output
possible_emissions = {}
possible_transitions = {}


def take_inventory():
    # input from sys
    for line in input_file:
        split_line = ["<s>/BOS"] + line.strip().split(" ") + ["</s>/EOS"]
        for i in range(len(split_line)):
            item = split_line[i]
            # by default, item is split by "/" which will capture the "/" in the word "</s>"
            if "</s>" in item:
                word = "</s>"
                tag = "EOS"
            else:
                pair = split_line[i].rsplit("/", maxsplit=1)
                word = pair[0]
                tag = pair[1]
            split_line[i] = (word, tag)  # modify split_line by replacing string with tuple

        for i in range(len(split_line)):
            count_transitions(split_line, i)
            count_emissions(split_line, i)

    # running on an ide
    # with open(input_file_name, "r") as input_file:
    #     for line in input_file:
    #         split_line = ["<s>/BOS"] + line.strip().split(" ") + ["</s>/EOS"]
    #         for i in range(len(split_line)):
    #             item = split_line[i]
    #             # by default, item is split by "/" which will capture the "/" in the word "</s>"
    #             if "</s>" in item:
    #                 word = "</s>"
    #                 tag = "EOS"
    #             else:
    #                 pair = split_line[i].rsplit(r"/", maxsplit=1)
    #                 word = pair[0]
    #                 tag = pair[1]
    #             split_line[i] = (word, tag)  # modify split_line by replacing string with tuple
    #
    #         for i in range(len(split_line)):
    #             count_transitions(split_line, i)
    #             count_emissions(split_line, i)


def count_transitions(split_line, i):
    word = split_line[i][0]
    tag = split_line[i][1]

    if tag not in tag_unigrams:
        tag_unigrams[tag] = [0, []]
        if tag != "EOS" and tag != "BOS":
            tag_unigrams[tag][1].append("<unk>")
    tag_unigrams[tag][0] += 1
    if word not in tag_unigrams[tag][1]:
        tag_unigrams[tag][1].append(word)

    pos_pos = ""
    for j in range(2):
        if i + j < len(split_line):
            pos_pos += split_line[i + j][1] + " "
    pos_pos = pos_pos.strip(" ")
    if len(pos_pos.split(" ")) == 2:
        # print("pos-pos ngram = " + pos_pos_ngram)
        if pos_pos not in tag_bigrams:
            tag_bigrams[pos_pos] = 0
        tag_bigrams[pos_pos] += 1

    pos_pos_pos = ""
    for j in range(3):
        if i + j < len(split_line):
            pos_pos_pos += split_line[i + j][1] + " "
            if len(split_line[i + j][1]) > 6:
                print("ERROR: found a word " + split_line[i + j][1] + " in state transition")
    pos_pos_pos = pos_pos_pos.strip()
    if len(pos_pos_pos.split(" ")) == 3:
        # make entry for transition_prob
        if pos_pos_pos not in tag_trigrams:
            tag_trigrams[pos_pos_pos] = 0
        tag_trigrams[pos_pos_pos] = tag_trigrams[pos_pos_pos] + 1

    if word not in word_unigrams:
        word_unigrams[word] = 0
    word_unigrams[word] += 1


def count_emissions(split_line, i):
    pos_word_ngram = ""
    for j in range(1, -1, -1):
        pos_word_ngram += split_line[i][j] + " "
    pos_word_ngram = pos_word_ngram.strip(" ")
    if len(pos_word_ngram.split(" ")) == 2:
        if pos_word_ngram not in emission_prob:
            emission_prob[pos_word_ngram] = [0, split_line[i][1]]
        emission_prob[pos_word_ngram] = [emission_prob[pos_word_ngram][0] + 1, split_line[i][1]]


def generate_unk_prob():
    with open(unk_prob_file_name, "r") as unk_prob_file:
        for line in unk_prob_file:
            split_line = line.strip().split()
            pos = split_line[0]
            prob = float(split_line[1])
            unk_prob[pos] = prob
        unk_prob["BOS"] = 0.0
        unk_prob["EOS"] = 0.0


def count_tag_occurrences():
    # get total number of pos tags in training
    global total_tag_types
    for unigram in tag_unigrams:
        total_tag_types += tag_unigrams[unigram][0]


def interpolate(tag1, tag2, tag3):
    # count(t3) / total number of unique tags
    prob_1g = tag_unigrams[tag3][0] / total_tag_types

    # count(t2, t3) / count(t2)
    prob_2g = 0  # prob is 0 if bigram is not found
    if tag2 + " " + tag3 in tag_bigrams:
        prob_2g = tag_bigrams[tag2 + " " + tag3] / tag_unigrams[tag2][0]

    # count(t1, t2, t3) / count(t1, t2)
    prob_3g = 0
    if tag1 + " " + tag2 not in tag_bigrams:
        if tag3 != "BOS":
            T = len(tag_unigrams) - 2
            prob_3g = 1 / (T + 1)
    else:  # t1 t2 is in training
        if tag1 + " " + tag2 + " " + tag3 in tag_trigrams:  # prob is 0 if trigram is not found
            prob_3g = tag_trigrams[tag1 + " " + tag2 + " " + tag3] / tag_bigrams[tag1 + " " + tag2]
    return l3 * prob_3g + l2 * prob_2g + l1 * prob_1g


def report():
    # sort pos tags alphabetically
    sorted_tag_unigrams_keys = sorted(tag_unigrams.keys())

    # generate transition probabilities
    for tag1 in sorted_tag_unigrams_keys:
        for tag2 in sorted_tag_unigrams_keys:
            for tag3 in sorted_tag_unigrams_keys:
                # print("analyzing " + tag1 + " " + tag2 + " " + tag3)
                p_hat = interpolate(tag1, tag2, tag3)
                smoothed_p_hat = float('{:.10f}'.format(p_hat))
                log_p_hat = float('{:.10f}'.format(math.log10(smoothed_p_hat)))
                possible_transitions[tag1 + "_" + tag2 + " " + tag2 + "_" + tag3] = [smoothed_p_hat, log_p_hat]
                t1_t2 = tag1 + "_" + tag2
                t2_t3 = tag2 + "_" + tag3
                tag_set.add(t1_t2)
                tag_set.add(t2_t3)

    # generate emission probabilities
    for tag1 in sorted_tag_unigrams_keys:
        for tag2 in sorted_tag_unigrams_keys:
            for word in tag_unigrams[tag2][1]:
                ngram = tag1 + "_" + tag2 + " " + word
                # print("analyzing " + ngram)
                if tag2 + " " + word in emission_prob:
                    numerator = emission_prob[tag2 + " " + word][0]
                    denominator = tag_unigrams[tag2][0]
                    prob = numerator / denominator
                    if tag2 in unk_prob:
                        prob = prob * (1 - unk_prob[tag2])
                else:
                    if tag2 in unk_prob:
                        prob = unk_prob[tag2]
                    else:
                        prob = 0
                log_prob = 0.0000000000
                if prob != 0:
                    log_prob = float('{:.10f}'.format(math.log10(prob)))
                possible_emissions[ngram] = [float('{:.10f}'.format(prob)), log_prob]
                # print()

    # report to console
    # print("state_num=" + str(len(tag_unigrams) ** 2))
    # print("sym_num=" + str(len(word_unigrams)))
    # print("init_line_num=1")
    # print("trans_line_num=" + str(len(possible_transitions)))
    # print("emiss_line_num=" + str(len(possible_emissions)))
    # print()
    # print("\\init")
    # print("BOS_BOS 1")
    # print()
    # print("\\transition")
    # sorted_transitions = sorted(possible_transitions.keys())
    # for item in sorted_transitions:
    #     print(item + " " + str(possible_transitions[item]))
    # print()
    # print("\\emission")
    # print()
    # sorted_emissions = sorted(possible_emissions.keys())
    # for item in sorted_emissions:
    #     print(item + " " + str(possible_emissions[item]))

    # report to output file
    with open(output_file_name, "w") as output_file:
        output_file.write("state_num=" + str(len(tag_set)) + "\n")
        output_file.write("sym_num=" + str(len(word_unigrams)) + "\n")
        output_file.write("init_line_num=1" + "\n")
        output_file.write("trans_line_num=" + str(len(possible_transitions)) + "\n")
        output_file.write("emiss_line_num=" + str(len(possible_emissions)) + "\n")
        output_file.write("\n")
        output_file.write("\\init" + "\n")
        output_file.write("BOS_BOS 1.0000000000 0.0000000000" + "\n")
        output_file.write("\n")
        output_file.write("\\transition" + "\n")
        sorted_transitions = sorted(possible_transitions.keys())
        for item in sorted_transitions:
            output_file.write(item + " " + str(possible_transitions[item][0]) + " " + str(possible_transitions[item][1]) + "\n")
        output_file.write("\n")
        output_file.write("\\emission" + "\n")
        sorted_emissions = sorted(possible_emissions.keys())
        for item in sorted_emissions:
            output_file.write(item + " " + str(possible_emissions[item][0]) + " " + str(possible_emissions[item][1])+ "\n")


# DRIVER
generate_unk_prob()
take_inventory()
count_tag_occurrences()
report()


