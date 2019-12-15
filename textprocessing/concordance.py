class Concordance:
    def __init__(self, query, text_i=None, pad_left=10, id=None, line_s=None):
        """
        Arguments:
            query: search term as a string
            text_i: index of text in Corpus.texts
            pad_left: whitespace padding on left concordance line
            id: id representing search query used to determine which window to populate results in
            lines_s: starting line of these lines among all lines
        """
        self.query = query
        self.id = id
        self.text_i = text_i
        self.pad_left = pad_left
        self.lines = []
        self.center_inds = []
        self.line_s = None
        self.line_e = None

    def max(self, i=1):
            return max(len(item[i].strip()) for item in self.lines)


    def add(self, conc_dict):
        line = ' '.join(conc_dict['left']), ' '.join(conc_dict['center']), ' '.join(conc_dict['right'])
        # self.line_e += 1
        first_ind = self.pad_left if self.pad_left > len(conc_dict['left']) else len(conc_dict['left'])
        second_ind = first_ind + len(conc_dict['center']) + 1
        self.center_inds.append((first_ind, second_ind))
        self.lines.append(line)

    def to_string(self, end='\n', delimiter='\t'):
        return ''.join('{left}{d}{center}{d}{right}\n'.format(
            left=left.rjust(self.pad_left),
            center=center,
            right=right,
            d=delimiter,
        ) for left, center, right in self.lines)
