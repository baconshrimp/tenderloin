tiles = {
    'wind-east': '\N{MAHJONG TILE EAST WIND}',
    'wind-south': '\N{MAHJONG TILE SOUTH WIND}',
    'wind-west': '\N{MAHJONG TILE WEST WIND}',
    'wind-north': '\N{MAHJONG TILE NORTH WIND}',
    'dragon-red': '\N{MAHJONG TILE RED DRAGON}',
    'dragon-green': '\N{MAHJONG TILE GREEN DRAGON}',
    'dragon-white': '\N{MAHJONG TILE WHITE DRAGON}',
    'characters-1': '\N{MAHJONG TILE ONE OF CHARACTERS}',
    'characters-2': '\N{MAHJONG TILE TWO OF CHARACTERS}',
    'characters-3': '\N{MAHJONG TILE THREE OF CHARACTERS}',
    'characters-4': '\N{MAHJONG TILE FOUR OF CHARACTERS}',
    'characters-5': '\N{MAHJONG TILE FIVE OF CHARACTERS}',
    'characters-6': '\N{MAHJONG TILE SIX OF CHARACTERS}',
    'characters-7': '\N{MAHJONG TILE SEVEN OF CHARACTERS}',
    'characters-8': '\N{MAHJONG TILE EIGHT OF CHARACTERS}',
    'characters-9': '\N{MAHJONG TILE NINE OF CHARACTERS}',
    'bamboo-1': '\N{MAHJONG TILE ONE OF BAMBOOS}',
    'bamboo-2': '\N{MAHJONG TILE TWO OF BAMBOOS}',
    'bamboo-3': '\N{MAHJONG TILE THREE OF BAMBOOS}',
    'bamboo-4': '\N{MAHJONG TILE FOUR OF BAMBOOS}',
    'bamboo-5': '\N{MAHJONG TILE FIVE OF BAMBOOS}',
    'bamboo-6': '\N{MAHJONG TILE SIX OF BAMBOOS}',
    'bamboo-7': '\N{MAHJONG TILE SEVEN OF BAMBOOS}',
    'bamboo-8': '\N{MAHJONG TILE EIGHT OF BAMBOOS}',
    'bamboo-9': '\N{MAHJONG TILE NINE OF BAMBOOS}',
    'circles-1': '\N{MAHJONG TILE ONE OF CIRCLES}',
    'circles-2': '\N{MAHJONG TILE TWO OF CIRCLES}',
    'circles-3': '\N{MAHJONG TILE THREE OF CIRCLES}',
    'circles-4': '\N{MAHJONG TILE FOUR OF CIRCLES}',
    'circles-5': '\N{MAHJONG TILE FIVE OF CIRCLES}',
    'circles-6': '\N{MAHJONG TILE SIX OF CIRCLES}',
    'circles-7': '\N{MAHJONG TILE SEVEN OF CIRCLES}',
    'circles-8': '\N{MAHJONG TILE EIGHT OF CIRCLES}',
    'circles-9': '\N{MAHJONG TILE NINE OF CIRCLES}',
    # 'flower-plum': '\N{MAHJONG TILE PLUM}',
    # 'flower-orchid': '\N{MAHJONG TILE ORCHID}',
    # 'flower-bamboo': '\N{MAHJONG TILE BAMBOO}',
    # 'flower-chrysanthemum': '\N{MAHJONG TILE CHRYSANTHEMUM}',
    # 'flower-spring': '\N{MAHJONG TILE SPRING}',
    # 'flower-summer': '\N{MAHJONG TILE SUMMER}',
    # 'flower-autumn': '\N{MAHJONG TILE AUTUMN}',
    # 'flower-winter': '\N{MAHJONG TILE WINTER}',
}
reverse_tiles = dict((value, key) for key, value in tiles.items())

deck = (
    [tile for tile in tiles.keys() if not tile.startswith('flower')] * 4
    # + [tile for tile in tiles.keys() if tile.startswith('flower')]
)

winds = ['east', 'south', 'west', 'north']
