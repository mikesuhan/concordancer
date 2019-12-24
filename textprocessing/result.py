class Result:

    # attributes in the order that they appear in the heading
    attrs = 'rank', 'tokens', 'freq', 'normed_freq', 'disp',
    delimiter = ' \t'

    def __init__(self, r_id, i, rank, tokens, freq, disp, tokens_n, norm_to=1000, rtype='Tokens', max_len=20):
        self.r_id = r_id
        self.i = i
        self.rank = rank
        self.tokens = tokens
        self.freq = freq
        self.disp = disp
        self.rtype = rtype
        self.max_len = max_len
        self.tokens_n = tokens_n
        self.norm_to = norm_to
        self.normed_freq = freq / tokens_n * norm_to



    def heading(self):
        return ('Rank  ',
                '{tokens:{pad}}'.format(tokens=self.rtype, pad=self.max_len),
                'Frequency',
                'Per {norm_to:,}'.format(norm_to=self.norm_to),
                'Dispersion')


    def row(self):
        return '{rank:<6,}{d}{tokens:<{t_pad}}{d}{freq:<9,}{d}{normed_freq:<{norm_pad},.2f}{d}{disp:<10,}\n'.format(
            rank=self.rank,
            tokens=self.tokens,
            t_pad=self.max_len,
            freq=self.freq,
            normed_freq=self.normed_freq,
            norm_pad=len('Per {norm_to:,}'.format(norm_to=self.norm_to)),
            disp=self.disp,
            d=self.delimiter
        )