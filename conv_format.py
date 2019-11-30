"""
Helper function for CSE 415 project, Dec 2019
Convert viterbi output for 3-gram
"""

import sys

def convert():

    def match_words_and_tags(words, tags):
        if len(tags) != len(words) + 1:
            print("Mismatch between tags and words")
            exit(-1)
        else:
            tagged_sentence = []
            for word in words:
                tag = tags[words.index(word) + 1].split("_")
                tag = tag[1]
                tagged_sentence.append(word + "/" + tag)
            return tagged_sentence


    def open_file():
        for line in sys.stdin:
            line = line.split("=>")
            words = line[0].split()
            tags = line[1].split()
            tags.pop(-1)
            tagged_sentence = match_words_and_tags(words, tags)
            print(" ".join(tagged_sentence))

    open_file()

convert()
