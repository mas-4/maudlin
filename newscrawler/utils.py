from datetime import datetime as dt

from celery import Celery

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def refactor(x, old, new):
    """Just y=mx+b !"""
    m = (new[1] - new[0]) / (old[1] - old[0])
    b = new[0] - m * old[0]
    return m * x  + b

def interpolate(color1='FF0000', color2='00FF00', factor=0.5):
    color1 = [int(color1[i:i+2], 16) for i in range(0, 6, 2)]
    color2 = [int(color2[i:i+2], 16) for i in range(0, 6, 2)]
    result = color1
    for i in range(0, 3):
        result[i] = round(result[i] + factor * (color2[i] - color1[i]));
    result = [format(n, 'x').zfill(2) for n in result]
    return ''.join(result)

def color(num, r=[-100,100], color1='FF0000', color2='00FF00'):
    c = interpolate(factor=refactor(num, r, [0,1]), color1=color1, color2=color2)
    return c

def pagination(c, m):
    current = c
    last = m
    delta = 2
    left = current - delta
    right = current + delta + 1
    rng = []
    rangeWithDots = []
    l = None

    for i in range(1, last+1):
        if i == 1 or i == last or i >= left and i < right:
            rng.append(i)

    for i in rng:
        if l:
            if i - l == 2:
                rangeWithDots.append(l + 1)
            elif i - l != 1:
                rangeWithDots.append('...')
        rangeWithDots.append(i)
        l = i

    return rangeWithDots

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def log_failure(*args):
    from newscrawler.config import Config
    with open(Config.LogFailPath, 'at') as fout:
        fout.write(' : '.join(str(dt.now()), *args))
