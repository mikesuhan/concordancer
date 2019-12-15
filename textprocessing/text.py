# -*- coding: utf-8 -*-

from re import finditer, IGNORECASE, sub, findall
# from mammoth import convert_to_html
from textprocessing.srt import parse_srt

from textprocessing.concordance import Concordance
from textprocessing.msword import read_docx



class Text:
    contractions = ("n't", "'ll", "'d", "'s", "'re", "'ve", "'m")
    punctuation = '!\,./:;?\\—'
    symbols = '#$%&*+<=>@^_`|~'
    enclosers = '\'"«‹»›„‚“‟‘‛’”’"❛❜❟❝❞⹂〝〞〟＂{}[]()'
    escapes = '\.^$*+?()[{|'
    titles = 'mr.', 'ms.', 'mrs.', 'mx.', 'jr.', 'sr.', 'rev.', 'fr.', 'br.', 'pr.', 'dr.', 'drs.', 'esq.', 'hon.', \
             'capt.', 'cmdr.', 'col.', 'cpl.', 'sgt.', 'st.', 'ave.', 'rd.', 'pl.', 'blvd.', 'mt.', 'sq.', 'co.', 'inc.', \
             'ltd.', 'est.', 'inst.', 'etc.'

    def __init__(self, data=None, filepath=None, category=None, filename=None, io=None):
        self.error = False
        self.filename = filename if filename else filepath
        self.filepath = filepath
        self.category = category

        if io:
            if filepath.endswith('.docx'):
                self.text = read_docx(io)
            elif filepath.endswith('.txt'):
                self.text = io.read().strip()
            elif filepath.endswith('.srt'):
                self.text = parse_srt(io.read())

        elif filepath:
            try:
                if filepath.endswith('.txt'):
                    with open(filepath, errors='ignore') as f:
                        self.text = f.read().strip()

                elif filepath.endswith('.docx'):
                    self.text = read_docx(filepath)

                elif filepath.endswith('.srt'):
                    with open(filepath, 'r') as f:
                        self.text = parse_srt(f.read())


            except UnicodeDecodeError:
                print('UnicodeDecodeError')
                self.text = ''
                self.error = True

        elif type(data) == str:
            self.text = data.strip()

        if type(self.text) == bytes:
            self.text = self.text.decode()

        if not self.category:
            self.category = 'Uncategorized'

    def __repr__(self):
        return self.text

    def count(self):
        return len(findall('\w+', self.text))

    def remove_html(self, text):
        return sub(r'</?[a-zA-Z]+/?>|<img src=".*?"\s?/?>', ' ', text)


    def word_tokenize(self, t, *funcs):
        for func in funcs:
            t = func(t)

        tokens = t.split()

        for i, token in enumerate(tokens):
            # punctuation at beginning of a word
            while len(tokens[i]) > 1 and tokens[i][0] in self.enclosers:
                if token.lower().startswith(self.contractions):
                    break
                # inserts removed punctuation before the token
                tokens.insert(i, tokens[i][0])
                i += 1
                tokens[i] = tokens[i][1:]

            # punctuation at end of a word
            while len(tokens[i]) > 1 and tokens[i][-1] in self.enclosers + self.punctuation:
                # avoids splitting . from titles, e.g.: dr., mr., ave.
                if tokens[i].lower() in self.titles:
                    break
                # avoids splitting punctuation followed by | operator used in search
                if tokens[i][-2] == '|':
                    break
                # avoids splitting . from acronyms and initialisms with . in the middle, e.g.: e.g., U.S.S.R., B.C.
                elif tokens[i][-1] == '.' and len(tokens[i]) % 2 == 0 and len(tokens[i]) >= 4:
                    if set(tokens[i][1::2]) == {'.'} and '.' not in set(tokens[i][0::2]):
                        break
                # Inserts removed punctuation after the token
                tokens.insert(i + 1, tokens[i][-1])
                tokens[i] = tokens[i][:-1]

            # self.contractions -- must come after punctuation is split from end of word
            for cont in self.contractions:
                if token.lower().endswith(cont) and token.lower() != cont:
                    tokens.insert(i + 1, tokens[i][-len(cont):])
                    tokens[i] = tokens[i][:-len(cont)]

        return tokens

    def re_word_tokenize(self, text):
        return findall('\w+', text.lower())

    def freq_dist(self):
        tokens = self.re_word_tokenize(self.text)
        return {token: tokens.count(token) for token in set(tokens)}

    def context(self, substring_left, substring_right, chars=1000):
        """
        Arguments:
            substring_left: left boundary of word
            substring_right: right boundary of word
            chars: maximum number of characters added to substring_right and subtracted from substring_left
        """
        if substring_left - chars > 0:
            left_context = self.text[substring_left - chars :substring_left].split(maxsplit=1)
            if left_context:
                left_context = left_context[-1]
        else:
            left_context = self.text[0:substring_left]

        center_context = self.text[substring_left:substring_right]

        if len(self.text) >= substring_right + chars:
            right_context = self.text[substring_right:substring_right + chars].rsplit(maxsplit=1)
            if right_context:
                right_context = right_context[0]
        else:
            right_context = self.text[substring_right:len(self.text)]


        return {
            'left_context': left_context,
            'center_context': center_context,
            'right_context': right_context
                }

    def concordance(self, substring, tokens_left=5, tokens_right=5, id=None, regexp=False):
        if 4 > tokens_left:
            left_max = 10
        elif 7 > tokens_left:
            left_max = 9
        else:
            left_max = 8

        left_max *= tokens_left

        substring_indices = finditer(r'\b' + substring + r'\b', self.text, IGNORECASE)
        #conc_lines = []
        c = Concordance(substring, pad_left=left_max, id=id)
        for substring_index in substring_indices:
            substring_left, substring_right = substring_index.span()
            conc_left = substring_left - 100 if substring_left - 100 > 0 else 0
            conc_right = substring_right + len(substring) + 100 if len(self.text) >= len(substring) + 100 else len(self.text)

            conc_line = {
                'left': self.word_tokenize(self.text[conc_left:substring_left])[1:][-tokens_left:] if tokens_left else [],
                'center': self.word_tokenize(self.text[substring_left:substring_right]),
                'right': self.word_tokenize(self.text[substring_right:conc_right])[:-1][:tokens_right] if tokens_right else [],
                'substring_left': substring_left,
                'substring_right': substring_right,
                'name': self.filename,
                'category': self.category,
            }

            #conc_lines.append(conc_line)
            c.add(conc_line)
        return c

