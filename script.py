posx = attributes['posx']
posy = attributes['posy']
movx = attributes['movx']
movy = attributes['movy']

def move(x=movx, y=movy):
    attributes['movx'] = x
    attributes['movy'] = y


if movx == 0 and movy == 0:
    move(1, 1)
elif posx <= -10 and posy <= -10:
    move(1, 1)
elif posx >= 10 and posy >= 10:
    move(-1, -1)
