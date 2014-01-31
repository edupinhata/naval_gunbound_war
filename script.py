import random

attributes['lookx'] = random.randrange(-1, 2)
attributes['looky'] = random.randrange(-1, 2)

if attributes['posx'] <= -20:
    attributes['movx'] = 1
elif attributes['posx'] >= 20:
    attributes['movx'] = -1
else:
    attributes['movx'] = random.randrange(-1, 2)

if attributes['posy'] <= -20:
    attributes['movy'] = 1
elif attributes['posy'] >= 20:
    attributes['movy'] = -1
else:
    attributes['movy'] = random.randrange(-1, 2)

if random.randrange(0, 2) == 1:
    shoot()
