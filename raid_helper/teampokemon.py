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
        pass
    elif type == 'poison':
        pass
    elif type == 'ground':
        pass
    elif type == 'rock':
        pass
    elif type == 'bug':
        pass
    elif type == 'ghost':
        pass
    elif type == 'steel':
        pass
    elif type == 'fire':
        pass
    elif type == 'water':
        pass
    elif type == 'grass':
        pass
    elif type == 'electric':
        pass
    elif type == 'psychic':
        pass

