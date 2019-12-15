def is_match(match_against, query, case_sensitive=False):
    """Determines if two lists of strings are matches."""
    if not case_sensitive:
        match_against = [w.lower() for w in match_against]
        query = [w.lower() for w in query]

    for i, token in enumerate(query):
        if '|' in token:
            for tok in token.split('|'):
                if is_string_match(tok, match_against[i]):
                    break
            else:
                return False
        elif not is_string_match(token, match_against[i]):
            return False

    return True

def is_string_match(query, match_against):
    negative_queries = []
    if '~' in query:
        negative_queries = query.split('~')
        if query[0] != '~':
            query = negative_queries[0]
        else:
            query = None
        # negative_queries[0] will either be a real query or will be ''
        del negative_queries[0]

    positive_match = False

    if query is not None:

        if query == match_against:
            positive_match = True
        elif query == '*':
            positive_match = True
        elif len(query) > 2 and query.startswith('*') and query.endswith('*') and query[1:-1] in match_against:
            positive_match = True
        elif query.startswith('*') and match_against.endswith(query[1:]):
            positive_match = True
        elif query.endswith('*') and match_against.startswith(query[:-1]):
            positive_match = True

    # requires either the lack of a normal query or the matching of a normal query
    if negative_queries and (positive_match or not query):
        for nq in negative_queries:
            if nq == match_against:
                return False
            elif is_asterix_match(nq, match_against):
                return False
        else:
            return True

    return positive_match



def is_asterix_match(query, match_against):
    if '*' not in query:
        return False
    elif query == '*':
        return True
    elif len(query) > 2 and query.startswith('*') and query.endswith('*') and query[1:-1] in match_against:
        return True
    elif query.startswith('*') and match_against.endswith(query[1:]):
        return True
    elif query.endswith('*') and match_against.startswith(query[:-1]):
        return True


    return False
