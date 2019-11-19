#!/usr/bin/python3
'''MilestoneA.py
This runnable file will provide a representation of
answers to key questions about your project in CSE 415.

'''

# DO NOT EDIT THE BOILERPLATE PART OF THIS FILE HERE:

CATEGORIES=['Baroque Chess Agent','Wicked Problem Formulation and A* Search',\
  'Backgammon Agent that Learns','Hidden Markov Models: Algorithms and Applications']

class Partner():
  def __init__(self, lastname, firstname, uwnetid):
    self.uwnetid=uwnetid
    self.lastname=lastname
    self.firstname=firstname

  def __lt__(self, other):
    return (self.lastname+","+self.firstname).__lt__(other.lastname+","+other.firstname)

  def __str__(self):
    return self.lastname+", "+self.firstname+" ("+self.uwnetid+")"

class Who_and_what():
  def __init__(self, team, option, title, approach, workload_distribution, references):
    self.team=team
    self.option=option
    self.title=title
    self.approach = approach
    self.workload_distribution = workload_distribution
    self.references = references

  def report(self):
    rpt = 80*"#"+"\n"
    rpt += '''The Who and What for This Submission

Project in CSE 415, University of Washington, Autumn, 2019
Milestone A

Team: 
'''
    team_sorted = sorted(self.team)
    # Note that the partner whose name comes first alphabetically
    # must do the turn-in.
    # The other partner(s) should NOT turn anything in.
    rpt += "    "+ str(team_sorted[0])+" (the partner who must turn in all files in Catalyst)\n"
    for p in team_sorted[1:]:
      rpt += "    "+str(p) + " (partner who should NOT turn anything in)\n\n"

    rpt += "Option: "+str(self.option)+"\n\n"
    rpt += "Title: "+self.title + "\n\n"
    rpt += "Approach: "+self.approach + "\n\n"
    rpt += "Workload Distribution: "+self.workload_distribution+"\n\n"
    rpt += "References: \n"
    for i in range(len(self.references)):
      rpt += "  Ref. "+str(i+1)+": "+self.references[i] + "\n"

    rpt += "\n\nThe information here indicates that the following file will need\n"+\
     "to be submitted (in addition to code and possible data files):\n"
    rpt += "    "+\
     {'1':"Baroque_Chess_Agent_Report",'2':"Wicked_Problem_Forulation_Report",\
      '3':"Backgammon_Agent_That_Learns_Report", '4':"Hidden_Markov_Models_Report"}\
        [self.option]+".pdf\n"

    rpt += "\n"+80*"#"+"\n"
    return rpt

# END OF BOILERPLATE.

# Change the following to represent your own information:

denise = Partner("Mak", "Denise", "dpm3")
vincent = Partner("Soesanto", "Vincent", "vsoes")
team = [denise, vincent]

OPTION = '4'
# Legal options are 1, 2, 4, and 4.

title = "Part-of-Speech Tagging using HMM"

approach = '''Our approach will be to first gather probabilities from a corpus that has been preprocessed with
    POS tags. Then we will implement the tagger using the Viterbi approach to HMM. We will then test the tagger
    with a held-out portion of the corpus'''

workload_distribution = '''Vincent: Preprocess corpus to extract relevant conditional probabilities to use for the 
    decoding task of HMM. Probabilities are extracted by counting ngrams. 
    Denise: Implementing HMM tagger using Viterbi algorithm to output the most likely part-of-speech
    tag sequence given an input.
'''

reference1 = '''Jurafsky, Daniel, and James H. Martin. 2009. Speech and Language Processing: 
    An Introduction to Natural Language Processing, Speech Recognition, and Computational Linguistics. 2nd edition. 
    Prentice-Hall.'''

reference2 = '''"Testing to see if this change is seen by master'''

our_submission = Who_and_what([denise, vincent], OPTION, title, approach, workload_distribution, [reference1, reference2])

# You can run this file from the command line by typing:
# python3 who_and_what.py

# Running this file by itself should produce a report that seems correct to you.
if __name__ == '__main__':
  print(our_submission.report())