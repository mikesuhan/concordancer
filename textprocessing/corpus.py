from zipfile import ZipFile
from io import BytesIO
from operator import itemgetter
from collections import defaultdict
from textprocessing.text import Text
from textprocessing.substring import Substring
from textprocessing.result import Result
from string import punctuation

from message import Message

punctuation += '”“’‘—'

class Corpus:

    text_proc_msg = 'Processing text {:,} of {:,}.'

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

    def ngram_dist(self, min_n, max_n, r_id, min_freq=5):
        frequencies = defaultdict(int)
        dispersions = defaultdict(list)
        tokens_n = 0
        max_len = 0

        for i, text in enumerate(self.texts):
            m = self.text_proc_msg.format(i + 1, len(self.texts))
            m = Message(m)
            self.queue.put(m)


            for n in range(min_n, max_n + 1):
                if n == 1:
                    for token in text.word_tokenize(text.text, str.lower):

                        if len(token) > max_len:
                            max_len = len(token)
                        frequencies[token] += 1
                        dispersions[token].append(i)
                if n > 1:
                    for ngram in text.ngrams(n):
                        ngram = ' '.join(ngram)
                        if len(ngram) > max_len:
                            max_len = len(ngram)
                        frequencies[ngram] += 1
                        dispersions[ngram].append(i)

            tokens_n += text.tokens_n

        nt = self.norm_to(tokens_n)
        rank = 1
        results = []

        if min_n == 1 and max_n == 1:
            rtype = 'Tokens'
        else:
            rtype = 'Ngrams'

        for i, (key, val) in enumerate(sorted(((k, frequencies[k]) for k in frequencies), key=itemgetter(1), reverse=True)):
            if min_freq > val:
                break

            if i == 0:
                prev_freq = val
            elif prev_freq > val:
                prev_freq = val
                rank += 1

            result = Result(r_id,
                            i,
                            rank,
                            key,
                            val,
                            len(set(dispersions[key])),
                            tokens_n, norm_to=nt,
                            rtype=rtype,
                            max_len=35)
            results.append(result)
            if len(results) == 100:
                self.queue.put(results)
                results = []

        if results:
            self.queue.put(results)

    def freq_dist(self, r_id, punct=False, min_freq=0):
        frequencies = defaultdict(int)
        dispersions = defaultdict(int)
        tokens_n = 0
        # types = []
        for i, text in enumerate(self.texts):
            m = self.text_proc_msg.format(i + 1, len(self.texts))
            m = Message(m)
            self.queue.put(m)
            max_len = 0

            tokens = text.word_tokenize(text.text, str.lower)

            for token in set(tokens):
                if not punct and token not in punctuation:
                    n = tokens.count(token)
                    frequencies[token] += n
                    dispersions[token] += 1
                    tokens_n += n
                    if len(token) > max_len:
                        max_len = len(token)

        nt = self.norm_to(tokens_n)
        rank = 1
        results = []

        for i, (key, val) in enumerate(sorted(((k, frequencies[k]) for k in frequencies), key=itemgetter(1), reverse=True)):
            if i == 0:
                prev_freq = val
            elif prev_freq > val:
                prev_freq = val
                rank += 1

            if min_freq > val:
                break
            result = Result(r_id,
                            i,
                            rank,
                            key,
                            val,
                            dispersions[key],
                            tokens_n,
                            norm_to=nt,
                            rtype='Tokens',
                            max_len=20)

            results.append(result)
            if len(results) == 100:
                self.queue.put(results)
                results = []
        if results:
            self.queue.put(results)


    @staticmethod
    def norm_to(n):
        return 10 ** (len(str(n)) - 1)
