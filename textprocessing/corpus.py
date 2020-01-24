import os
from json import dumps
from zipfile import ZipFile
from io import BytesIO
from operator import itemgetter
from collections import defaultdict
from textprocessing.text import Text
from textprocessing.substring import Substring
from textprocessing.result import Result
from string import punctuation
from re import findall, sub
from message import Message

punctuation += '”“’‘—'

class Corpus:

    text_proc_msg = 'Processing text {:,} of {:,}.'
    ignore_exts = '.nfo',

    def __init__(self, gui_obj):
        self.gui_obj = gui_obj
        self.queue = gui_obj.queue
        self.text_paths = []
        self.texts = []
        self.i = 0

    def next(self):
        if len(self.texts) < self.i + 1:
            self.i += 1
        else:
            self.i = 0

        return self.texts[self.i]

    def load_string(self, str_input):
        if not self.texts:
            self.texts = []
        self.texts.append(Text(data=str_input))
        self.text_paths.append('Manually Entered Text')
        m = Message('Manually input text loaded.')
        self.queue.put(m)



    def load_texts(self, *text_paths):
        text_count = 0
        if not self.texts:
            self.texts = []
        for tp in text_paths:
            if tp not in self.text_paths:
                if tp.endswith('.zip'):
                    with ZipFile(tp) as zip:
                        for fn in [f for f in zip.namelist() if not f.endswith(self.ignore_exts)]:
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

        added_texts = [t.title for t in self.texts[-len(text_paths):]]
        return Message(m, added_texts=added_texts)


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

    def ngram_dist(self, opts, r_id):
        min_freq = 5
        frequencies = defaultdict(int)
        dispersions = defaultdict(list)
        tokens_n = 0
        max_len = 0

        if findall('[*+|]', opts['filter']):
            opts['filter'] = Substring(opts['filter'].strip())
        else:
            opts['filter'] = Text().word_tokenize(opts['filter'], str.lower)

        for i, text in enumerate(self.texts):
            m = self.text_proc_msg.format(i + 1, len(self.texts))
            m = Message(m)
            self.queue.put(m)

            for n in range(opts['ngrams']['min_len'], opts['ngrams']['max_len'] + 1):
                    for ngram in text.ngrams(n, no_punct=opts['no_punct']['checked'], filter=opts['filter']):
                        ngram = ' '.join(ngram)
                        if len(ngram) > max_len:
                            max_len = len(ngram)
                        frequencies[ngram] += 1
                        dispersions[ngram].append(i)

            tokens_n += text.tokens_n


        if not opts['norm_rate']:
            opts['norm_rate'] = self.norm_to(tokens_n)

        rank = 1
        results = []

        if opts['ngrams']['min_len'] == 1 and opts['ngrams']['max_len'] == 1:
            rtype = 'Tokens'
        else:
            rtype = 'Ngrams'

        prev_freq = None

        for i, (key, freq) in enumerate(sorted(((k, frequencies[k]) for k in frequencies), key=itemgetter(1), reverse=True)):
            if opts['frequency']['min'] > freq:
                break
            elif opts['frequency']['max'] and freq > opts['frequency']['max']:
                continue

            if opts['dispersion']['checked']:
                disp = len(set(dispersions[key]))
                if opts['dispersion']['min'] > disp:
                    continue
                elif opts['dispersion']['max'] and disp > opts['dispersion']['max']:
                    continue
            else:
                disp = None

            if opts['rate']['checked']:
                rate = freq / tokens_n * opts['norm_rate']
                if opts['rate']['min'] > rate:
                    break
                elif opts['rate']['max'] and rate > opts['rate']['max']:
                    continue
            else:
                rate = None

            if opts['rank']['checked']:

                if prev_freq is None:
                    prev_freq = freq
                elif prev_freq > freq:
                    prev_freq = freq
                    rank += 1

                if opts['rank']['min'] > rank:
                    continue
                elif opts['rank']['max'] and rank > opts['rank']['max']:
                    break

            else:
                rank = None



            result = Result(r_id,
                            i,
                            rank,
                            key,
                            freq,
                            rate,
                            disp,
                            tokens_n, norm_to=opts['norm_rate'],
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

    def save(self, zip_fp):
        with ZipFile(zip_fp, 'w') as zip:
            text_data = {}
            for i, text in enumerate(self.texts):
                if text.filepath:
                    fn = os.path.split(text.filepath)[-1]
                elif text.title:
                    fn = sub('[^a-zA-Z0-1 \-_()]', '', text.title)
                    fn += '.txt'
                else:
                    fn = 'text ' + str(i) + '.txt'

                zip.writestr(fn, text.text)
                print(fn, text.text[:50])

                text_data[fn] = {
                    'filename': fn,
                    'title': text.title,
                }

            zip.writestr('text_data.json', dumps(text_data))
            zip.writestr('chat_settings.json', dumps(self.gui_obj.chat_settings))
            zip.writestr('instructions.json', dumps(self.gui_obj.instructions.instructions))




    @staticmethod
    def norm_to(n):
        return 10 ** (len(str(n)) - 1)
