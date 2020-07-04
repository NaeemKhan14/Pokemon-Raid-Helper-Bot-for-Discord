def weaknessCheck(dict, type):
    if type == 'normal':
        dict['fighting'] -= 2
        dict['ghost'] += 2
    elif type == 'fighting':
        dict['flying'] -= 2
        dict['rock'] += 2
        dict['bug'] += 2
        dict['psychic'] -= 2
        dict['dark'] += 2
        dict['fairy'] -= 2
    elif type == 'flying':
        dict['fighting'] += 2
        dict['ground'] += 2
        dict['rock'] -= 2
        dict['bug'] += 2
        dict['grass'] += 2
        dict['electric'] -= 2
        dict['ice'] -= 2
    elif type == 'poison':
        dict['fighting'] += 2
        dict['poison'] += 2
        dict['ground'] -= 2
        dict['bug'] += 2
        dict['grass'] += 2
        dict['psychic'] -= 2
        dict['fairy'] += 2
    elif type == 'ground':
        dict['poison'] += 2
        dict['rock'] += 2
        dict['water'] -= 2
        dict['grass'] -= 2
        dict['electric'] += 2
        dict['ice'] -= 2
    elif type == 'rock':
        dict['normal'] -= 2
        dict['fighting'] -= 2
        dict['flying'] -= 2
        dict['poison'] -= 2
        dict['ground'] -= 2
        dict['steel'] -= 2
        dict['fire'] -= 2
        dict['water'] -= 2
        dict['grass'] -= 2
    elif type == 'bug':
        dict['fighting'] += 2
        dict['flying'] -= 2
        dict['ground'] += 2
        dict['rock'] -= 2
        dict['fire'] -= 2
        dict['grass'] += 2
    elif type == 'ghost':
        dict['normal'] += 2
        dict['fighting'] += 2
        dict['poison'] += 2
        dict['bug'] += 2
        dict['ghost'] -= 2
        dict['dark'] -= 2
    elif type == 'steel':
        dict['normal'] += 2
        dict['fighting'] -= 2
        dict['flying'] += 2
        dict['poison'] += 2
        dict['ground'] -= 2
        dict['rock'] += 2
        dict['bug'] += 2
        dict['steel'] += 2
        dict['fire'] -= 2
        dict['grass'] += 2
        dict['psychic'] += 2
        dict['ice'] += 2
        dict['dragon'] += 2
        dict['fairy'] += 2
    elif type == 'fire':
        dict['ground'] -= 2
        dict['rock'] -= 2
        dict['bug'] += 2
        dict['steel'] += 2
        dict['fire'] += 2
        dict['water'] -= 2
        dict['grass'] += 2
        dict['ice'] += 2
        dict['fairy'] += 2
    elif type == 'water':
        dict['steel'] += 2
        dict['fire'] += 2
        dict['water'] += 2
        dict['grass'] -= 2
        dict['electric'] -= 2
        dict['ice'] += 2
    elif type == 'grass':
        dict['flying'] -= 2
        dict['poison'] -= 2
        dict['ground'] += 2
        dict['bug'] -= 2
        dict['fire'] -= 2
        dict['water'] += 2
        dict['grass'] += 2
        dict['electric'] += 2
        dict['ice'] -= 2
    elif type == 'electric':
        dict['flying'] += 2
        dict['ground'] -= 2
        dict['steel'] += 2
        dict['electric'] += 2
    elif type == 'psychic':
        dict['fighting'] += 2
        dict['bug'] -= 2
        dict['ghost'] -= 2
        dict['psychic'] += 2
        dict['dark'] -= 2
    elif type == 'ice':
        dict['fighting'] -= 2
        dict['rock'] -= 2
        dict['steel'] -= 2
        dict['fire'] -= 2
        dict['ice'] += 2
    elif type == 'dragon':
        dict['fire'] += 2
        dict['water'] += 2
        dict['grass'] += 2
        dict['electric'] += 2
        dict['ice'] -= 2
        dict['dragon'] -= 2
        dict['fairy'] -= 2
    elif type == 'dark':
        dict['fighting'] -= 2
        dict['bug'] -= 2
        dict['ghost'] += 2
        dict['psychic'] += 2
        dict['dark'] += 2
        dict['fairy'] -= 2
    elif type == 'fairy':
        dict['fighting'] += 2
        dict['poison'] -= 2
        dict['bug'] += 2
        dict['steel'] -= 2
        dict['dragon'] += 2
        dict['dark'] += 2
