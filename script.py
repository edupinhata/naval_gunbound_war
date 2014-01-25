if attributes['movx'] == 0:
    attributes['movx'] = 1
elif attributes['posx'] >= 10:
    attributes['movx'] = -1
elif attributes['posx'] <= -10:
    attributes['movx'] = 1
