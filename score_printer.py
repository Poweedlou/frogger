from os.path import exists


start_text = '''WINNERS:\n'''


def create_file():
    with open('score.txt', 'w') as fo:
        fo.write(start_text)


def read_score():
    if not exists('score.txt'):
        create_file()
    with open('score.txt', 'r') as fi:
        lines = dict(map(lambda s: reversed(s.split(') ', maxsplit=1)[1].rsplit(': ', maxsplit=1)), list(filter(bool, map(str.strip, fi.readlines())))[1:]))
    print(lines)


def add_score(score):
    read_score()


read_score()