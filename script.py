import random

if attributes['posx'] <= -10:
    attributes['movx'] = 1
elif attributes['posx'] >= 10:
    attributes['movx'] = -1
else:
    attributes['movx'] = random.randrange(-1, 2)

if attributes['posy'] <= -10:
    attributes['movy'] = 1
elif attributes['posy'] >= 10:
    attributes['movy'] = -1
else:
    attributes['movy'] = random.randrange(-1, 2)

if random.randrange(0, 2) == 1:
    shoot()
