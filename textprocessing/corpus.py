from zipfile import ZipFile
from io import BytesIO
from collections import defaultdict
from textprocessing.text import Text
from textprocessing.matcher import is_match
from textprocessing.concordance import  Concordance
from textprocessing.substring import Substring
from string import punctuation

from message import Message

class Corpus:
    def __init__(self, queue):
        self.queue = queue
        self.text_paths = []
        self.texts = []
        self.i = 0

    def next(self):
        if len(self.texts) < self.i + 1:
            self.i += 1
        else:
            self.i = 0

        return self.texts[self.i]

    def load_texts(self, *text_paths):
        text_count = 0
        if not self.texts:
            self.texts = []
        for tp in text_paths:
            if tp not in self.text_paths:
                if tp.endswith('.zip'):
                    with ZipFile(tp) as zip:
                        for fn in zip.namelist():
                            with zip.open(fn) as f:
                                self.text_paths.append(fn)
                                self.texts.append(Text(filepath=fn, io=BytesIO(f.read()), id=text_count))
                                text_count += 1


                else:
                    self.text_paths.append(tp)
                    self.texts.append(Text(filepath=tp, id=text_count))
                    text_count += 1
        m = '{:,} text{} loaded.'.format(
            text_count,
            's' if text_count > 1 else ''
        )

        return Message(m)



    def concordance(self, query, left_len=5, right_len=5, conc_id=None, case_sensitive=False, limit=None):
        """Adds one concordance object to queue per text."""
        word_count = 0
        m = Message('Starting concordance process.')
        self.queue.put(m)
        print('conc_id', conc_id)

        query = Substring(query).regexp_substring
        lines_n = 0
        texts_len = len(self.texts)



        for k, text in enumerate(self.texts):
            # concordance = Concordance(query_str, k, left_max, id=conc_id, line_s=lines_n)
            # text.word_tokenize(text.text, str.lower)
            word_count += text.count()

            if lines_n == limit:
                break

            conc = text.concordance(query, left_len, right_len, conc_id=conc_id)
            if conc.lines:
                conc.line_s = lines_n
                conc.text_i = k
                lines_n += len(conc.lines)
                self.queue.put(conc)

            if len(self.texts) > k:

                m = Message('{}/{}. {} processed.'.format(
                    k + 1,
                    len(self.texts),
                    self.text_paths[k]
                ))
                self.queue.put(m)

        m = Message('Processed {:,} tokens in {:,} text{}. {:,} matches found.'.format(
            word_count,
            len(self.texts),
            '' if len(self.texts) == 1 else 's',
            lines_n
        ), conc_finished=True,
        tag='red')

        self.queue.put(m)

    def freq_dist(self, punct=False):
        frequencies = defaultdict(int)
        dispersions = defaultdict(int)
        tokens_n = 0
        # types = []
        for i, text in enumerate(self.texts):
            m = 'Processing text {:,} of {:,}.'.format(i + 1, len(self.texts))
            m = Message(m)
            self.queue.put(m)

            tokens = text.word_tokenize(text.text, str.lower)
            for token in set(tokens):
                if not punct and token not in punctuation:
                    n = tokens.count(token)
                    frequencies[token] += n
                    dispersions[token] += 1
                    tokens_n += n
            # types += list(fd.keys())
            # types = list(set(types))

        # types_n = len(types)

        results = {
            'results': sorted(((k, frequencies[k], dispersions[k]) for k in frequencies), key=lambda x: x[1], reverse=True),
            'tokens_n': tokens_n,
            'texts_n': i + 1
            # 'types_n': types_n
        }

        self.queue.put(results)
        m = 'Frequency list ready.'
        m = Message(m, tag='red')
        self.queue.put(m)

    @staticmethod
    def norm_to(n):
        return 10 ** (len(str(n)) - 1)
