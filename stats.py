'''Тут записываются все очки'''

from os.path import exists


def reader(s):
    s = list(reversed(s.split(') ', maxsplit=1)[1].rsplit(': ', maxsplit=1)))
    s[0] = int(s[0])
    return s


def create_file(scores=None):
    with open('score.txt', 'w', encoding='u8') as fo:
        fo.write('Leaderboard:\n')
        if scores is not None:
            for pos, s in enumerate(scores):
                s, n = s
                fo.write(f'{pos + 1}) {n}: {s}\n')


def read_score():
    if not exists('score.txt'):
        create_file()
    with open('score.txt', 'r') as fi:
        data = fi.readlines()[1:]
    s = map(reader, filter(bool, map(lambda x: x.strip('\n'), data)))
    return list(s)


def add_score(score, name):
    scores = read_score()
    scores.append((score, name))
    scores.sort(key=lambda x: -x[0])
    if len(scores) > 9:
        scores = scores[:10]
    create_file(scores)
