'''
check_hmm.py

Vincent Soesanto
CSE 415
Autumn 2019

This script reads in a state-emission HMM file, checks its format, and outputs a warning file.

Usage: check_hmm.sh input_hmm > warning_file
'''
import sys

# command line arguments
input_file_name = sys.argv[1]

# for home development
# input_file_name = "wsj_hmm_3g"
# input_file_name = "examples/hmm_ex2"

# global variables
claimed = {}
actual = {}
report = []


def extract_hmm():
    init = False
    transition = False
    emission = False
    actual_states = set()
    actual_syms = set()
    state_transitions = {}
    emission_transitions = {}

    with open(input_file_name, "r") as input_file:
        for line in input_file:
            line = line.strip("\n").strip("\t")
            if line == "":
                continue

            if "state_num" in line:
                claimed["state_num"] = int(line.split("=")[1])
            elif "sym_num" in line:
                claimed["sym_num"] = int(line.split("=")[1])
            elif "init_line_num" in line:
                claimed["init_line_num"] = int(line.split("=")[1])
            elif "trans_line_num" in line:
                claimed["trans_line_num"] = int(line.split("=")[1])
            elif "emiss_line_num" in line:
                claimed["emiss_line_num"] = int(line.split("=")[1])
            elif line == "\\init":
                init = True
            elif line == "\\transition":
                transition = True
                init = False
            elif line == "\\emission":
                emission = True
                transition = False
            elif init:
                if "init_line_num" not in actual:
                    actual["init_line_num"] = 0
                actual["init_line_num"] += 1
            elif transition:
                if "trans_line_num" not in actual:
                    actual["trans_line_num"] = 0
                actual["trans_line_num"] += 1

                # take inventory of unique pos
                line = line.split()
                found_pos = False
                for item in line:
                    if not isfloat(item):
                        actual_states.add(item)
                    else:
                        break

                # add up probabilities
                history = line[0]
                for i in range(len(line)):
                    if isfloat(line[i]):
                        if history not in state_transitions:
                            state_transitions[history] = 0
                        state_transitions[history] += float(line[i])
                        break
            elif emission:
                if "emiss_line_num" not in actual:
                    actual["emiss_line_num"] = 0
                actual["emiss_line_num"] += 1

                # take inventory of unique words
                line = line.split()
                history = ""
                for i in range(len(line) - 1, -1, -1):
                    current = line[i]
                    if isfloat(current) and current[0] == '0':
                        actual_syms.add(line[i - 1])
                        history = line[i - 2]
                        if history not in emission_transitions:
                            emission_transitions[history] = 0
                        emission_transitions[history] += float(current)
                        break


    actual["state_num"] = len(actual_states)
    actual["states"] = actual_states
    actual["sym_num"] = len(actual_syms)
    actual["syms"] = actual_syms
    actual["state_transitions"] = state_transitions
    actual["emission_transitions"] = emission_transitions
    # print(actual["state_transitions"])
    # print(actual["emission_transitions"])


def evaluate():
    for commonality in ["state_num", "sym_num", "init_line_num", "trans_line_num", "emiss_line_num"]:
        inconsistent = False
        if actual[commonality] != claimed[commonality]:
            inconsistent = True
        report.append(warning_statement("line_num", commonality, None, inconsistent))

    for state in actual["state_transitions"]:
        if actual["state_transitions"][state] > 1.000000001 or actual["state_transitions"][state] <= 0.9:
            report.append(warning_statement("prob_sum", "trans_prob_sum", state, None))

    for state in actual["states"]:
        inconsistent = False
        if state in actual["emission_transitions"]:
            if actual["emission_transitions"][state] > 1.000000001 or actual["emission_transitions"][state] <= 0.9:
                report.append(warning_statement("prob_sum", "emiss_prob_sum", state, inconsistent))
        else:
            inconsistent = True
            report.append(warning_statement("prob_sum", "emiss_prob_sum", state, inconsistent))

    for item in report:
        print(item)


def warning_statement(type, commonality, state, inconsistent):
    if type == "line_num":
        if inconsistent:
            return "warning: different numbers of " + commonality + ": claimed=" + str(claimed[commonality])\
                   + ", real=" + str(actual[commonality])
        else:
            return commonality + "=" + str(actual[commonality])

    if type == "prob_sum":
        inventory = "state_transitions"
        if commonality == "emiss_prob_sum":
            inventory = "emission_transitions"
        if inconsistent:
            return "warning: the " + commonality + " for state " + state + " is 0.0000000000"
        else:
            return "warning: the " + commonality + " for state " + state + " is " + str('{:.10f}'.format(actual[inventory][state]))


def isfloat(str):
    try:
        float(str)
    except ValueError:
        return False
    return True


# DRIVER
extract_hmm()
evaluate()

















