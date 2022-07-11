from enum import auto
from functools import reduce
from typing import Dict, Set

from .category import Category
from .utils.enum import AutoStrEnum
from .utils.parsing import MaxiMunchTokenFinder


class TokenCategory(AutoStrEnum):
  # "dummy" to block false positives, see below
  BLOCK = auto()

  # tokens that have precedence over the suggestions below
  NULLIFIES_OMNI = auto()
  NULLIFIES_OMNI_AND_VEGETARIAN = auto()

  # tokens that suggest certain categories
  SUGGESTS_VEGAN = auto()
  SUGGESTS_VEGAN_OR_VEGETARIAN = auto()
  SUGGESTS_VEGETARIAN = auto()
  SUGGESTS_VEGAN_OR_OMNI = auto()
  SUGGESTS_VEGAN_VEGETARIAN_OR_OMNI = auto()
  SUGGESTS_VEGETARIAN_OR_OMNI = auto()
  SUGGESTS_OMNI = auto()

categories_to_tokens: Dict[TokenCategory, Set[str]] = {
  # the only purpose of these is to block false positives in actual categories,
  # e.g. fat which suggests animal or plant fat, whereas "fat free" doesn't tell
  # us anything about the category
  TokenCategory.BLOCK: {
    "approx",
    "defatted",
    "fat free",
    "fate",
    "low fat",
    "lowfat",
    "no added fat",
    "no fat added",
    "nonfat",
    "oxidant",
    "reduced fat",
    "spray",
    "% fat",
  },

  TokenCategory.NULLIFIES_OMNI: {
    'meatless',
    'vegetarian',
  },

  TokenCategory.NULLIFIES_OMNI_AND_VEGETARIAN: {
    'plant based',
    'plant-based',
    'vegan',
  },

  TokenCategory.SUGGESTS_VEGAN: {
    'agave', 'almond', 'almond milk', 'amaranth',
    'apple', 'apricot', 'artichoke', 'asparagus', 'aubergine', 'avocado',
    'banana', 'barley', 'basil', 'bean', 'beans, kidney', 'beet',
    'berries', 'berry', 'beer', 'black russian', 'bread',
    'broccoli', 'bulgur', 'bruschetta',
    'cabbage', 'cactus', 'canola', 'cantaloupe', 'carrot', 'cashew', 'celery',
    'chamomile', 'chard', 'cherry', 'cherries', 'chive', 'cider', 'cilantro',
    'cocoa', 'coffee', 'cola', 'collard', 'corn', 'couscous',
    'cress', 'cucumber', 'currant',
    'daiquiri', 'dasheen', 'date', 'dill',
    'edamame', 'eggplant',
    'energy drink',
    'falafel', 'fennel', 'fig', 'flour', 'flower', 'fries', 'fruit',
    'jam', 'juice',
    'garlic', 'gimlet', 'gin', 'ginger',
    'grain', 'grape', 'greens', 'guacamole', 'guava', 'gum',
    'hard candy', 'hummus',
    'kale', 'ketchup', 'kidney bean', 'kohlrabi', 'kumquat',
    'leaf', 'leaves', 'leek', 'lemon', 'lentil', 'lettuce',
    'lime', 'liqueur', 'luffa', 'lychee',
    'macadamia', 'malt', 'mango',
    'margarine', 'margarita', 'marmalade', 'martini', 'melon',
    'millet', 'mimosa', 'mint', 'miso', 'molasses', 'mushroom', 'mustard',
    'natto', 'nectarine', 'noodle', 'nut', 'nut butter', 'nut meat',
    'oat', 'oat milk', 'old fashioned', 'olive', 'onion', 'orange',
    'pakora', 'papaya', 'parsley', 'parsnip', 'pasta',
    'pea', 'pecan', 'peel', 'pepper', 'persimmon',
    'pickle', 'pigeon peas', 'pimiento', 'pita',
    'plant', 'plantain', 'plum', 'pomegranate', 'potato',
    'pretzel', 'prune', 'pumpkin',
    'quinoa',
    'radicchio', 'radish', 'raisin', 'rhubarb', 'rice', 'rice cake',
    'roll', 'root', 'rum',
    'sauerkraut', 'screwdriver', 'seed', 'seitan', 'sesame', 'shoot',
    'soy', 'soy milk', 'soymilk', 'spinach',
    'soda', 'soft drink', 'sports drink', 'sprout', 'squash', 'sugar', 'syrup',
    'tabbouleh', 'tahini', 'tamarind', 'tangerine', 'tannier', 'tea', 'tequila',
    'tempeh', 'tofu', 'tomato', 'tortilla', 'truffle', 'turnip',
    'vegan', 'vegetable', 'vinegar', 'vodka',
    'wasabi', 'water', 'weed', 'wheat', 'whiskey',
    'yam', 'yeast',
    'zucchini', 'zwieback',
  },

  TokenCategory.SUGGESTS_VEGAN_OR_VEGETARIAN: {
    'bar',
    'candy, nfs', 'chutney', 'cocktail, nfs', 'cracker', 'crouton',
    'dip',
    'formula',
    'meatless',
    'nougat',
    'pesto', 'pop', 'porridge',
    'scone', 'strudel',
  },

  TokenCategory.SUGGESTS_VEGETARIAN: {
    'baklava', 'banana split', 'biscuit', 'borscht', 'butter',
    'cake', 'cappuccino', 'caramel', 'chocolate', 'cheese',
    'cobbler', 'confection fat', 'cookie',
    'cream', 'creme', 'crepe', 'croissant', 'custard',
    'egg',
    'frost', 'french toast', 'fudge',
    'gelato',
    'honey',
    'icing',
    'kefir',
    'latte',
    'macchiato', 'mayonnaise', 'milk', 'milkfat',
    'mocha', 'mousse', 'mozzarella', 'muffin',
    'paneer', 'pastry', 'pie', 'pizza', 'praline', 'pudding',
    'ranch',
    'tiramisu', 'toffee', 'trifle', 'tzatziki',
    'vegetarian',
    'waffle', 'whey', 'whipped', 'white russian',
    'yogurt',
  },

  TokenCategory.SUGGESTS_VEGAN_OR_OMNI: {
    'jelly',
  },

  TokenCategory.SUGGESTS_VEGAN_VEGETARIAN_OR_OMNI: {
    'dumpling',
    'fat',
    'general mills',
    'kellogg',
    'kimchi',
    'post',
    'quaker',
    'ravioli, ns',
    'sandwich, nfs', 'soup, nfs', 'stew, nfs', 'sushi, nfs',
    'wine',
  },

  TokenCategory.SUGGESTS_VEGETARIAN_OR_OMNI: set(),

  TokenCategory.SUGGESTS_OMNI: {
    'adobo', 'anchovy', 'animal',
    'bacon', 'barracuda', 'bass', 'bear', 'beaver', 'beef',
    'bison', 'bologna', 'brain', 'burger',
    'caribou', 'carp', 'casserole', 'chicken', 'chorizo', 'clam',
    'cod', 'crab', 'croaker',
    'deer', 'dog', 'dove', 'duck',
    'eel',
    'fish', 'flounder', 'frog',
    'gelatin', 'gizzard', 'goat', 'goulash', 'gravy', 'ground hog',
    'haddock', 'halibut', 'herring', 'ham', 'jerky',
    'kidney',
    'lamb', 'lard', 'liver', 'lobster',
    'mackerel', 'marshmallow', 'matzo', 'meat', 'meringue',
    'mollusk', 'moose', 'mortadella', 'mullet', 'mussel',
    'nacho',
    'octopus', 'okra', 'opossum', 'ostrich', 'oyster', 'ox',
    'pad thai', 'pastrami', 'pepperoni', 'pepperpot', 'perch',
    'pig', 'pike', 'pheasant', 'porgy', 'pork', 'pot roast', 'potato skins',
    'poultry',
    'quail',
    'rabbit', 'raccoon', 'ray', 'roe',
    'salami', 'salmon', 'sardine', 'sausage', 'scallop', 'seafood',
    'shark', 'shrimp', 'snail', 'souffle', 'squid', 'squirrel',
    'steak', 'sturgeon',
    'thuringer', 'tilapia', 'tongue', 'tripe', 'trout',
    'tuna', 'turkey', 'turtle',
    'veal', 'venison',
    'whiting', 'wurst',
  },
}

nullification_mappings = {
  TokenCategory.NULLIFIES_OMNI: {
    TokenCategory.SUGGESTS_OMNI: TokenCategory.SUGGESTS_VEGAN_OR_VEGETARIAN,
    TokenCategory.SUGGESTS_VEGAN_OR_OMNI: TokenCategory.SUGGESTS_VEGAN,
    TokenCategory.SUGGESTS_VEGAN_VEGETARIAN_OR_OMNI: (
      TokenCategory.SUGGESTS_VEGAN_OR_VEGETARIAN
    ),
    TokenCategory.SUGGESTS_VEGETARIAN_OR_OMNI: (
      TokenCategory.SUGGESTS_VEGETARIAN
    ),
  },
  TokenCategory.NULLIFIES_OMNI_AND_VEGETARIAN: {
    token_category: TokenCategory.SUGGESTS_VEGETARIAN
    for token_category in categories_to_tokens.keys()
  },
}

all_tokens: Set[str] = reduce(
  lambda x, y: x | y,
  categories_to_tokens.values(),
  set()
)

all_tokens_finder = MaxiMunchTokenFinder(all_tokens)

def categorize(description: str) -> Category:
  names_in_desc = all_tokens_finder.find_all(description.lower())

  found_token_categories = {
    category for category, tokens in categories_to_tokens.items()
    if any(name in tokens for name in names_in_desc)
  }

  for nullification_category in [
    TokenCategory.NULLIFIES_OMNI, TokenCategory.NULLIFIES_OMNI_AND_VEGETARIAN
  ]:
    if nullification_category not in found_token_categories:
      continue
    nullification_mapping = nullification_mappings[nullification_category]
    found_token_categories = {
        token_category for token_category in {
        (
          token_category
          if token_category not in nullification_mapping
          else nullification_mapping[token_category]
        ) for token_category in found_token_categories
      }
      if token_category is not None
    }

  if TokenCategory.SUGGESTS_OMNI in found_token_categories:
    return Category.OMNI
  if TokenCategory.SUGGESTS_VEGETARIAN_OR_OMNI in found_token_categories:
    return Category.VEGETARIAN_OR_OMNI
  if TokenCategory.SUGGESTS_VEGAN_VEGETARIAN_OR_OMNI in found_token_categories:
    if TokenCategory.SUGGESTS_VEGETARIAN in found_token_categories:
      return Category.VEGETARIAN_OR_OMNI
    return Category.VEGAN_VEGETARIAN_OR_OMNI
  if TokenCategory.SUGGESTS_VEGAN_OR_OMNI in found_token_categories:
    if TokenCategory.SUGGESTS_VEGETARIAN in found_token_categories:
      return Category.VEGETARIAN_OR_OMNI
    return Category.VEGAN_OR_OMNI
  if TokenCategory.SUGGESTS_VEGETARIAN in found_token_categories:
    return Category.VEGETARIAN
  if TokenCategory.SUGGESTS_VEGAN_OR_VEGETARIAN in found_token_categories:
    return Category.VEGAN_OR_VEGETARIAN
  if TokenCategory.SUGGESTS_VEGETARIAN in found_token_categories:
    return Category.VEGETARIAN
  if TokenCategory.SUGGESTS_VEGAN in found_token_categories:
    return Category.VEGAN
  return Category.UNCATEGORIZED
