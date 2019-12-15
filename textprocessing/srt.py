def parse_srt(text):
    return '\n'.join(' '.join(segment.split('\n')[2:]) for segment in text.split('\n\n'))