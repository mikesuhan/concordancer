from re import split

class Substring:
    def __init__(self, substring):
        self.substring = substring
        self.mysql_substring = self.make_regexp(substring, r'[[:<:]]', r'[[:>:]]', r'[[:space:]]')
        self.regexp_substring = self.make_regexp(substring, r'\b', r'\b', r'\s')

    def make_regexp(self, substring, lb, rb, space, recursion=False):
        parenthesis_delimited_substring = [item for item in split('(\(.+?\))', substring) if item]

        if len(parenthesis_delimited_substring) > 1:
            print(parenthesis_delimited_substring)
            substring = ' '.join(self.make_regexp(item.strip(), lb, rb, space, True)
                                 for item in parenthesis_delimited_substring)

        elif '|' in substring and not substring.startswith('|') and not substring.endswith('|'):
            substrings = substring.split('|')
            substring = '|'.join(self.make_regexp(s, lb, rb, space, True) for s in substrings)

        elif '_' in substring and not set(ch for ch in substring if ch not in ' _()'):
            print('enclosed _ detected', substring)
            substring = substring.replace('_', r'[a-z0-9\\\'\-]+')


        elif ' _ ' in substring:
            substrings = substring.split()
            for i, substring in enumerate(substrings):
                if substring.strip() == '_':
                    substrings[i] = r'[a-z0-9\\\'\-]+'

            # making regexp for spaces will occur in a recursion of make_regexp
            substring = ' '.join(substrings)
            substring = self.make_regexp(substring, lb, rb, space, True)

        elif '*' in substring or '+' in substring:
            substrings = substring.split()

            # match ZERO or more characters at beginning of substring -- matches forms starting with token and token
            for i, substring in enumerate(substrings):
                if substring.endswith('*)'):
                    substring = r'{st}[a-z0-9]*)'.format(st=substring[:-2])
                if substring.endswith('*'):
                    # With MySQL regexp, \b is [[:<:]] and [[:>:]] for start and end of word boundaries
                    substring = r'{st}[a-z0-9]*'.format(st=substring[:-1])

                # match ZERO or more characters at beginning of substring -- matches forms ending with token and token
                if substring.startswith('(*'):
                    substring = r'([a-z0-9]*{st}'.format(st=substring[2:])
                if substring.startswith('*'):
                    substring = r'[a-z0-9]*{st}'.format(st=substring[1:])

                # match ONE or more character at end of substring' -- matches starting with token but not token
                if substring.endswith('+)'):
                    substring = r'{st}[a-z0-9]+)'.format(st=substring[:-2])
                if substring.endswith('+'):
                    substring = r'{st}[a-z0-9]+'.format(st=substring[:-1])

                # match ONE or more character at beginning of substring -- matches forms ending with token but not token
                if substring.startswith('(+'):
                    substring = r'([a-z0-9]+{st}'.format(st=substring[2:])
                if substring.startswith('+'):
                    substring = r'[a-z0-9]+{st}'.format(st=substring[1:])

                #substring = r'{lb}{st}{rb}'.format(st=substring, lb=lb, rb=rb)
                substrings[i] = substring

            substring = ' '.join(substrings)

        if not recursion:
            substrings = substring.split()
            for i, substring in enumerate(substrings):
                """
                if substring.startswith('(') and len(substring) > 1:
                    substring = r'({lb}{st}'.format(lb=lb, st=substring[1:])
                else:
                    substring = r'{lb}{st}'.format(lb=lb, st=substring)
                if substring.endswith(')') and len(substring) > 1:
                    substring = r'{st}{rb})'.format(st=substring[:-1], rb=rb)
                else:
                    substring = r'{st}{rb}'.format(st=substring, rb=rb)
                """

                substring = r'{lb}{st}{rb}'.format(lb=lb, st=substring, rb=rb)


                substrings[i] = substring

            substring = space.join(substrings)
        return substring