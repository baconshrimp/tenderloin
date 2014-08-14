raw_tiles = {
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
    'flower-plum': '\N{MAHJONG TILE PLUM}',
    'flower-orchid': '\N{MAHJONG TILE ORCHID}',
    'flower-bamboo': '\N{MAHJONG TILE BAMBOO}',
    'flower-chrysanthemum': '\N{MAHJONG TILE CHRYSANTHEMUM}',
    'flower-spring': '\N{MAHJONG TILE SPRING}',
    'flower-summer': '\N{MAHJONG TILE SUMMER}',
    'flower-autumn': '\N{MAHJONG TILE AUTUMN}',
    'flower-winter': '\N{MAHJONG TILE WINTER}',
}


class Tile(object):
    """Represents a Mahjong tile."""

    def __init__(self, code, symbol):
        self.code = code
        self.symbol = symbol
        self.suite, self.value = code.split('-', 1)

    def __hash__(self):
        return hash(self.symbol)

    def __eq__(self, other):
        return other is not None and self.symbol == other.symbol

    def __lt__(self, other):
        return other is not None and self.symbol < other.symbol

    def prev(self, num=1):
        """Returns the previous ordered tile if applicable."""
        return None

    def next(self, num=1):
        """Returns the next ordered tile if applicable."""
        return None


class NumericTile(Tile):
    """Represents a numeric Mahjong tile."""

    def __init__(self, code, symbol):
        super(NumericTile, self).__init__(code, symbol)
        self.value = int(self.value)

    def prev(self, num=1):
        """Returns the previous ordered tile if applicable."""
        return tile_names.get('{}-{}'.format(self.suite, self.value - num))

    def next(self, num=1):
        """Returns the next ordered tile if applicable."""
        return tile_names.get('{}-{}'.format(self.suite, self.value + num))


class SpecialTile(Tile):
    """Represents any non-numeric Mahjong tile."""
    pass


def make_tile(name, symbol):
    if name.split('-', 1)[0] in ('characters', 'circles', 'bamboo'):
        return NumericTile(name, symbol)
    else:
        return SpecialTile(name, symbol)


tile_names = {name: make_tile(name, symbol)
              for name, symbol in raw_tiles.items()}
tile_symbols = {tile.symbol: tile for tile in tile_names.values()}
tiles = {tile: name for name, tile in tile_names.items()}

deck = (
    [tile for tile in tile_names.values() if tile.suite != 'flower'] * 4
    + [tile for tile in tile_names.values() if tile.suite == 'flower']
)

winds = ['east', 'south', 'west', 'north']


def serialize(hand):
    """Serializes a list of tiles into a list of tile codes."""
    return [tiles.get(tile) for tile in hand]


def deserialize(hand):
    """Deserializes a list of tile codes into a list of tiles."""
    return [tile_names.get(name) for name in hand]
