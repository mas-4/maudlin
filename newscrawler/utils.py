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
