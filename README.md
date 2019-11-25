# Hidden Markov Model Part-of-Speech Tagger

This repository contains the framework for a Hidden Markov Model (HMM) implementation of an English part-of-speech tagger. The training data is a segment of the Wall Street Journal corpus.

## Extracting probabilities

Run the following command to extract bigram emission and transition probabilities:

```bash
cat training_data | create_2gram_hmm.sh output_2gram_hmm
```

Run the following command to extract trigram emission and transition probabilities:

```bash
cat training_data | create_3gram_hmm.sh output_3gram_hmm l1 l2 l3 unk_prob_file
```

- Sample ```training data``` provided in this repository is ```toy_input``` under ```examples/toy```. 
- The smoothing technique used is [linear interpolation](https://en.wikipedia.org/wiki/Linear_interpolation), where ```l1```, ```l2```, ```l3``` are lambda values. 
- Probabilities in ```unk_prob_file``` are used to account for unknown words. Sample ```unk_prob_file``` provided in this repository is ```toy_unk``` under ```examples/toy```. 


## Train and test sets

- The data used to train the tagger is ```wsj_sec0.word_pos```
- The ```unk_prob_file``` used during training is ```unk_prob_sec22``` 
- The test set used to evaluate the tagger is ```wsj_sec22.word_pos```

All of these files can be found under ```examples```.
