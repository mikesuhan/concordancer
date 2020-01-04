def dictgetter(d):
    """Iterates through embedded dictionary, calling get() method on every value. Ensures every value is an int."""
    for key in d:
        if type(d[key]) is not dict:
            d[key] = d[key].get()
            if type(d[key]) == str and d[key].isdigit():
                d[key] = int(d[key])
            elif type(d[key]) != int and key != 'filter':
                d[key] = 0
        else:
            d[key] = dictgetter(d[key])

    return d