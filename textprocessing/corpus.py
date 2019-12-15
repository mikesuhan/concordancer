from zipfile import ZipFile
from io import BytesIO
from textprocessing.text import Text
from textprocessing.matcher import is_match
from textprocessing.concordance import  Concordance
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
        print(text_paths)
        text_count = 0
        if not self.texts:
            self.texts = []
        for tp in text_paths:
            print(tp)
            if tp not in self.text_paths:
                if tp.endswith('.zip'):
                    with ZipFile(tp) as zip:
                        for fn in zip.namelist():
                            with zip.open(fn) as f:
                                self.text_paths.append(fn)
                                self.texts.append(Text(filepath=fn, io=BytesIO(f.read())))
                                text_count += 1


                else:
                    self.text_paths.append(tp)
                    self.texts.append(Text(filepath=tp))
                    text_count += 1
        m = '{:,} text{} loaded.'.format(
            text_count,
            's' if text_count > 1 else ''
        )

        return Message(m)



    def concordance(self, query, left_len=5, right_len=5, conc_id=None, case_sensitive=False, limit=None):
        """Adds one concordance object to queue per text."""
        word_count = 0
        print(self.text_paths)
        m = Message('Starting concordance process.')
        self.queue.put(m)

        # query_str = query.strip()
        # query = query.strip().split()
        lines_n = 0
        texts_len = len(self.texts)



        for k, text in enumerate(self.texts):
            # concordance = Concordance(query_str, k, left_max, id=conc_id, line_s=lines_n)
            # text.word_tokenize(text.text, str.lower)
            word_count += text.count()

            if lines_n == limit:
                break

            conc = text.concordance(query, left_len, right_len, id=conc_id)
            if conc.lines:
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
            word_count,    # todo make a new way to count tokens
            len(self.texts),
            '' if len(self.texts) == 1 else 's',
            lines_n
        ), conc_finished=True,
        tag='red')

        self.queue.put(m)



