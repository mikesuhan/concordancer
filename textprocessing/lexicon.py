CONTRACTIONS = ["n't", "'ll", "'d", "'s", "'re", "'ve", "'m"]
PUNCTUATION = '!\,./:;?\\—'
SYMBOLS = '#$%&*+<=>@^_`|~'
ENCLOSERS = '\'"«‹»›„‚“‟‘‛’”’"❛❜❟❝❞⹂〝〞〟＂{}[]()'
ESCAPEES = '\.^$*+?()[{|'

with open('titles.txt', encoding='UTF-8') as f:
    TITLES = f.read().strip().split()

STYLIZED_SINGLE_QUOTES = "‘‛’’❛❜"



NEW_CONTRACTIONS = []
for SSQ in STYLIZED_SINGLE_QUOTES:
    for C in CONTRACTIONS:
        NEW_CONTRACTIONS.append(C.replace("'", SSQ))

CONTRACTIONS += NEW_CONTRACTIONS
CONTRACTIONS = tuple(CONTRACTIONS)