# -*- coding: utf-8 -*-
import os
from re import finditer, IGNORECASE, sub, findall, match
from textprocessing.srt import parse_srt

from textprocessing.concordance import Concordance
from textprocessing.msword import read_docx
from textprocessing.substring import Substring


class Text:
    contractions = ("n't", "'ll", "'d", "'s", "'re", "'ve", "'m")
    punctuation = '-!\,./:;?\\—'
    symbols = '#$%&*+<=>@^_`|~'
    enclosers = '\'"«‹»›„‚“‟‘‛’”’"❛❜❟❝❞⹂〝〞〟＂{}[]()'
    non_alphanumeric = punctuation + symbols + enclosers
    escapes = '\.^$*+?()[{|'
    titles = 'mr.', 'ms.', 'mrs.', 'mx.', 'jr.', 'sr.', 'rev.', 'fr.', 'br.', 'pr.', 'dr.', 'drs.', 'esq.', 'hon.', \
             'capt.', 'cmdr.', 'col.', 'cpl.', 'sgt.', 'st.', 'ave.', 'rd.', 'pl.', 'blvd.', 'mt.', 'sq.', 'co.', 'inc.', \
             'ltd.', 'est.', 'inst.', 'etc.'

    def __init__(self, data=None, filepath=None, title=None, io=None, id=None, cache_tokens=True):
        self.error = False
        self.filepath = filepath
        self.id = id

        self.cached_tokens = []
        self.cache_tokens = cache_tokens
        self.tokens_n = 0

        self.text = ''

        if title:
            self.title = title
        elif filepath:
            self.title = os.path.split(filepath)[-1]
        elif id is not None:
            self.title = 'Text ' + id
        else:
            self.title = 'Text'

        if io:
            if filepath.endswith('.docx'):
                self.text = read_docx(io)
            elif filepath.endswith('.txt'):
                self.text = io.read().decode('utf-8').strip()
            elif filepath.endswith('.srt'):
                self.text = io.read().decode('utf-8')
                self.text = parse_srt(self.text)

        elif filepath:
            try:


                if filepath.endswith('.docx'):
                    self.text = read_docx(filepath)

                elif filepath.endswith('.srt'):
                    with open(filepath, encoding='utf-8') as f:
                        self.text = parse_srt(f.read())
                else:
                    with open(filepath, errors='ignore', encoding='utf-8') as f:
                        self.text = f.read().strip()


            except UnicodeDecodeError:
                print('UnicodeDecodeError')
                self.text = ''
                self.error = True

        elif type(data) == str:
            self.text = data.strip()

        if type(self.text) == bytes:
            self.text = self.text.decode()


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

        if self.cache_tokens:
            self.cached_tokens = tokens

        self.tokens_n = len(tokens)
        return tokens

    def ngrams(self, n, use_cache=True, no_punct=False, filter=None):
        if use_cache and self.cached_tokens:
            tokens = self.cached_tokens
        else:
            tokens = self.word_tokenize(self.text, str.lower)

        end = -1 if -n+1 == 0 else -n+1

        if type(filter) == Substring:
            for i, token in enumerate(tokens[:end]):
                ngram = ' '.join(tokens[i:i+n])
                if findall(filter.regexp_substring, ngram):
                    yield tokens[i:i+n]
        else:
            flen = 0 if filter is None else len(filter)
            for i, token in enumerate(tokens[:end]):
                y = True
                if no_punct or filter:
                    for k, tok in enumerate(tokens[i:i+n]):
                        if no_punct and tok in self.non_alphanumeric:
                            y = False
                            break
                        elif filter and tokens[i:i+n][k:k+flen] == filter:
                            y = True
                            break
                    else:
                        if filter:
                            y = False

                if y:
                    yield tuple(tokens[i:i+n])

    def re_word_tokenize(self, text):
        return findall("[\w'\-]+", text.lower())

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

    def concordance(self, substring, tokens_left=5, tokens_right=5, conc_id=None, regexp=False):
        if 4 > tokens_left:
            left_max = 10
        elif 7 > tokens_left:
            left_max = 9
        else:
            left_max = 8

        left_max *= tokens_left

        substring_indices = finditer(r'\b' + substring + r'\b', self.text, IGNORECASE)
        #conc_lines = []
        c = Concordance(substring, pad_left=left_max, text_i=self.id, id=conc_id, tokens_left=tokens_left)
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
                'name': self.filepath,
            }

            c.add(conc_line)
        return c

