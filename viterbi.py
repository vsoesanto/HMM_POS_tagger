"""
Viterbi Algorithm
CSE 415 project, 11/29/2019

Usage:
python viterbi.py hmm_filename inputfilename outputfilename

  * the HMM file must be in format created by the other script.
  * input file is a text file with one sentence per line.
    If omitted, gets input at command line by prompting user
  * output file is where output indicating the best parse found for
    the input sentence(s) is saved.

Example command line arguments:
3g_hmm the_store.txt output.txt
"""


import sys
import math
import numpy as np
import svgwrite

SPACING = 150
RADIUS = 44

def init_drawing(sentence, len=10):
    '''

    :param sentence: name based on the sentence or line being diagrammed
    :param sentence: length of sentence or line, to determine width
    :return: the drawing object named for the line being diagrammed
    '''
    name = sentence + '.svg'
    dwg = svgwrite.Drawing(name, profile='tiny', size=(len*SPACING,len*SPACING))
    return dwg

def draw_word(dwg, word, coords):
    dwg.add(dwg.text(word,
                     insert=coords, font_size="15px", fill='blue'))


def draw_state(dwg, log_prob=-5.12, state_name = "BOS_NNP", center=(100,100)):
    '''

    :param dwg:
    :param log_prob:
    :param state_name:
    :param center:
    :return:
    '''
    radius = RADIUS
    center_offset = 30
    right_side = (center[0]+ radius, center[1])
    dwg.add(dwg.circle(center, radius, stroke='blue', stroke_width=3, fill='none'))
    dwg.add(dwg.text(state_name,
                     insert=(center[0]-center_offset, center[1]+center_offset/2), font_size="15px", fill='red'))
    dwg.add(dwg.text("p={:.2f}".format(log_prob),
                     insert=(center[0]-center_offset, center[1]-center_offset/2), font_size="15px", fill='black'))

    dwg.save()
    return (state_name, right_side)


input_text_file = ''
output_text_file = 'output.txt'
if len(sys.argv) >= 4:
    output_text_file = sys.argv[3] # assume third argument is output file name

if len(sys.argv) > 3:
    input_text_file = sys.argv[2]
def read_hmm():

    states_key = {}
    states_index = {}
    emissions_key = {}
    init_key = {}
    init_lines = []

    def open_hmm():
        init = False
        transition = False
        emission = False
        states_key_counter = 0
        emissions_key_counter = 0

        with open(sys.argv[1], "r") as file:
            for line in file:
                line = line[:-1]
                if line == "":
                    continue
                elif line.startswith("state_num="):
                    state_num = int(line.split("=")[1])
                elif line.startswith("sym_num="):
                    sym_num = int(line.split("=")[1])
                elif line.startswith("init_line_num="):
                    init_line_num = int(line.split("=")[1])
                elif line.startswith("\\init"):
                    init = True
                elif line.startswith("\\transition"):
                    init = False
                    transition = True
                    transitions_array = np.full((state_num, state_num), -np.inf)
                elif line.startswith("\\emission"):
                    transition = False
                    emission = True
                    emissions_array = np.full((sym_num, state_num), -np.inf)
                elif init == True and line[-1].isdigit():
                    line = line.split()
                    start_prob = line[1]
                    start_state = line[0]
                    init_key[start_state] = float(start_prob)
                    init_lines.append(line)
                elif transition == True and line[-1].isdigit():
                    line_full = line
                    line = line.split()
                    if float(line[2]) > 1 or float(line[2]) < 0:
                        sys.stderr.write("warning: the prob is not in [0,1] range:{}".format(line_full))
                    state1 = line[0]
                    state2 = line[1]
                    if len(line) > 3:
                        prob = float(line[3])
                    else:
                        prob = math.log10(float(line[2]))
                        # prob = float(line[2]) # NOTE: in this case, not using log probabilities
                    if state1 not in states_key.keys():
                        states_key[state1] = states_key_counter
                        states_index[states_key_counter] = state1
                        states_key_counter +=1
                    if state2 not in states_key.keys():
                        states_key[state2] = states_key_counter
                        states_index[states_key_counter] = state2
                        states_key_counter += 1
                    i = states_key[state1]
                    j = states_key[state2]
                    transitions_array[i, j] = prob
                elif emission == True and line[-1].isdigit():
                    line_full = line
                    line = line.split()
                    if float(line[2]) > 1 or float(line[2]) < 0:
                        sys.stderr.write("warning: the prob is not in [0,1] range:{}".format(line_full))
                    word = line[1]
                    if word not in emissions_key.keys():
                        emissions_key[word] = emissions_key_counter
                        emissions_key_counter +=1
                    # emission_lines.append(line)
                    if len(line) > 3:
                        word = line[1]
                        state = line[0]
                        prob = float(line[3])
                    else:
                        word = line[1]
                        state = line[0]
                        prob = math.log10(float(line[2]))
                    i = emissions_key[word]
                    j = states_key[state]
                    emissions_array[i, j] = prob

                else:
                    continue
            try:
                k = emissions_key["<unk>"]
                # print(np.shape(np.argwhere(emissions_array[k, :] > -np.inf)))
            except Exception as e:
                print("Warning: No unknown found when loading HMM: {}".format(e))
        return transitions_array, emissions_array

    # open_hmm()

    def store_initials():
        init_probs = {}
        for init in init_lines:
            init_state = states_key[init[0]]
            init_prob = math.log10(float(init[1]))
            init_probs[init_state] = init_prob
        return init_probs

    transitions, emissions = open_hmm()
    init_probs = store_initials()

    return init_probs, states_key, states_index, emissions_key, transitions, emissions

def print_trellis(trellis):
    return

def viterbi(sentence, pi, states_key, states_index, emissions_key, transitions, emissions, line_count=0):

    def run_viterbi(sentence, line_num=0):
        # create diagram for this sentence
        dwg = init_drawing("line"+str(line_num))

        # Create trellis and backpointer matrices
        sentence = sentence.split()

        word_index = {}
        index_word = {}
        index = 0
        for word in sentence:
            index_word[index] = word
            word_index[word] = index
            index += 1
        s = len(sentence) + 1
        trans = len(transitions)
        trellis = np.full((trans,s), -np.inf)
        backpointers = np.full((trans,s), -1) #(fill backpointer array with dummy pointer -1)

        # Initialize array
        trellis_diagram_layers = []
        for n in range(trans):
            if n in pi.keys():
                trellis[n,0] = pi[n]
                trellis_layer_line0 = {}
                draw_word(dwg, 'START', (SPACING-(RADIUS), SPACING-100))
                (st_name, rt_side) = draw_state(dwg, 1, states_index[n],
                                                (SPACING * (0 + 1), SPACING * 1))
                trellis_layer_line0[states_index[n]] = rt_side # save right side coords
        trellis_diagram_layers.append(trellis_layer_line0)


        # Recursive procedure to fill array
        for t in range(s-1):
            # build string to print for this word's trellis layer
            trellis_layer_string = ''
            # hash for drawing lines in diagram
            trellis_layer_lines = {}
            j_found_count = 0  # for use in spacing out trellis diagram

            # Find all cells with values for i-th element - previous cells' probabilities
            prev_probs = trellis[:,t]
            prev_probs = np.where(prev_probs != -np.inf)[0]

            # Get the index of the current word, or <unk> if not in emissions table
            current_word = index_word[t]
            draw_word(dwg, current_word, (SPACING*(t+2)-(.8*RADIUS), SPACING - 100))
            if current_word in emissions_key.keys():
                k = emissions_key[current_word]
            else:
                try:
                    k = emissions_key["<unk>"] # TODO: BUG - WHAT IF NO UNK IN FILE?
                except Exception as e:
                    print("Warning: Word = {}: No unknown probability found with key = {}".format(current_word, e))
            for j in range(trans):
                if emissions[k,j] == -np.inf:
                    continue
                max_prob = -np.inf
                max_trans_emit_p = -np.inf
                max_pointer = -1
                for i in prev_probs:
                    if transitions[i,j] != -np.inf:
                        trans_emit_p = transitions[i,j] + emissions[k,j]
                        temp = trellis[i,t] + trans_emit_p #+ transitions[i,j] + emissions[k,j]
                        if temp > max_prob:
                            max_prob = temp
                            max_trans_emit_p = trans_emit_p
                            max_pointer = i  # comes from i

                trellis[j,t+1] = max_prob

                # Printing and drawing
                # we can print at time t+1, word current_word, state j coming from max_pointer if max_prob!=-inf
                if not max_prob == -np.inf:
                    j_found_count +=1
                    source = states_index[max_pointer]
                    state = states_index[j]  # we've just added this state
                    trellis_layer_string += "[{} (p={:.2f}, from {})]".format(
                        state, max_trans_emit_p, source)

                    (st_name, rt_side) = draw_state(dwg, max_trans_emit_p, state,
                               (SPACING*(t+2), SPACING*j_found_count))
                    # draw lines connecting to previous layer
                    dest_pt = trellis_diagram_layers[t][source]
                    left_side = (rt_side[0]-(2*RADIUS), rt_side[1])
                    dwg.add(dwg.line(left_side, dest_pt, stroke=svgwrite.rgb(10, 10, 16, '%')))
                    dwg.save()
                    trellis_layer_lines[st_name] = rt_side

                # update backpointers
                backpointers[j,t+1] = max_pointer

            # done with for j loop,
            print(current_word + ": " + trellis_layer_string)  #print the trellis layer
            # add new states to row t of trellis diagram layers
            trellis_diagram_layers.append(trellis_layer_lines)

        # Backtrace best path
        out = []

        # Get best final state
        j = np.argmax(trellis[:,s-1],axis=0)
        best_final_state_prob = trellis[j,s-1]
        out.append(states_index[j])

        for t in range(s-1, 0, -1):
            i = backpointers[j,t]
            if (i > -1):
                out.append(states_index[i])
            j = i
        out.reverse()
        return " ".join(out), best_final_state_prob

    output = run_viterbi(sentence, line_num=line_count)
    return output


def get_output_string(line, v_out):
    '''
    Creates a string for output of a line of input followed by its parse
    and its log probabability
    :param line: The line of input. Generally should be a sentence.
    :param v_out: A tuple (parse, lg_prob)
      The parse is a string like: BOS_BOS BOS_DT DT_NN NN_VBD VBD_JJ JJ_NN
      The lg_prob is a negative number like: -17.547289547289.
    :return:
      Example: the store sold expensive goods => BOS_BOS BOS_DT DT_NN NN_VBD VBD_JJ JJ_NNS -17.142151925332413
    '''
    # return line[:-1] + " => " + v_out[0] + " " + str(v_out[1]) + "\n"
    return line.strip() + " => " + v_out[0] + " " + str(v_out[1]) + "\n"

'''
Load the HMM
'''
pi, states_key, states_index, emissions_key, transitions, emissions = read_hmm()


with open(output_text_file, "w") as out: # always logging our output
    if not input_text_file == '':
        with open(input_text_file, "r") as file:
            line_count = 0
            for line in file:
                line_count += 1
                v_out = viterbi(line, pi, states_key, states_index, emissions_key, transitions, emissions, line_count=line_count)
                out.write(get_output_string(line, v_out))
                print(get_output_string(line, v_out))   # also print to screen

do_exit = False
while not do_exit:
    response = input("Enter a sentence to parse. (to quit, enter 'exit' or 'q')")
    if response == "exit" or response == 'q':
        do_exit = True
    else:
        v_out = viterbi(response, pi, states_key, states_index, emissions_key, transitions, emissions)
        print(get_output_string(response, v_out))
