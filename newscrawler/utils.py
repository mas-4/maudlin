def color(num):
    h = (num*155) / 100
    h += 100
    h = abs(h)
    d = format(int(h), 'x')
    d = d.zfill(2)
    if num > 0:
        color = f'00{d}00'
    else:
        color = f'{d}0000'
    return color


def gradient(num):
    p = (num*155) / 100
    p += 100
    p = abs(p)
    n = abs(255-p)
    p = format(int(p), 'x')
    p = p.zfill(2)
    n = format(int(n), 'x')
    n = n.zfill(2)
    if num < 0:
        color = f'{n}{p}00'
    else:
        color = f'{p}{n}00'
    return color
