def parse_srt(text):
    new_text = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.isdigit() or '-->' in line:
            continue
        else:
            new_text.append(line)
    return '\n'.join(new_text)