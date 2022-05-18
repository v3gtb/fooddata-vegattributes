from dataclasses import dataclass
from enum import auto
from functools import cached_property, reduce
from typing import Dict, Set, Union

from .fooddata import FoodDataDict
from .utils.enum import AutoStrEnum
from .utils.parsing import MaxiMunchTokenFinder

class Category(AutoStrEnum):
  VEGAN = auto()
  VEGAN_OR_VEGETARIAN = auto()
  VEGETARIAN = auto()
  VEGAN_OR_OMNI = auto()
  VEGAN_VEGETARIAN_OR_OMNI = auto()
  VEGETARIAN_OR_OMNI = auto()
  OMNI = auto()
  UNCATEGORIZED = auto()

categories_to_tokens: Dict[Union[Category, str], Set[str]] = {
  # the only purpose of these is to block false positives in actual categories,
  # e.g. fat which suggests animal or plant fat, whereas "fat free" doesn't tell
  # us anything about the category
  "block": {
    "fat free",
    "low fat",
    "no added fat",
    "no fat added",
    "nonfat"
  },

  Category.VEGAN: {
    'agave', 'almond', 'almond milk', 'amaranth',
    'apple', 'apricot', 'artichoke', 'asparagus', 'aubergine', 'avocado',
    'banana', 'barley', 'basil', 'bean', 'beet',
    'berries', 'berry', 'beer', 'black russian', 'bread',
    'broccoli', 'bulgur', 'bruschetta',
    'cabbage', 'cactus', 'canola', 'cantaloupe', 'carrot', 'cashew', 'celery',
    'chard', 'cherry', 'cherries', 'chive', 'cider', 'cilantro',
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
    'natto', 'nectarine', 'noodle', 'nut', 'nut butter',
    'oat', 'oat milk', 'old fashioned', 'olive', 'onion', 'orange',
    'pakora', 'papaya', 'parsley', 'parsnip', 'pasta',
    'pea', 'pecan', 'peel', 'pepper', 'persimmon',
    'pickle', 'pimiento', 'pita',
    'plant', 'plantain', 'plum', 'pomegranate', 'potato',
    'pretzel', 'prune', 'pumpkin',
    'quinoa',
    'radicchio', 'radish', 'raisin', 'rhubarb', 'rice', 'rice cake',
    'roll', 'root', 'rum',
    'sauerkraut', 'screwdriver', 'seed', 'seitan', 'sesame', 'shoot',
    'soy', 'soy milk', 'spinach',
    'soda', 'soft drink', 'sports drink', 'sprout', 'squash', 'sugar', 'syrup',
    'tabbouleh', 'tahini', 'tamarind', 'tangerine', 'tannier', 'tea', 'tequila',
    'tempeh', 'tofu', 'tomato', 'tortilla', 'truffle', 'turnip',
    'vegetable', 'vinegar', 'vodka',
    'wasabi', 'water', 'weed', 'wheat', 'whiskey',
    'yam', 'yeast',
    'zucchini', 'zwieback',
  },

  Category.VEGAN_OR_VEGETARIAN: {
    'bar',
    'candy, nfs', 'chutney', 'cocktail, nfs', 'cracker', 'crouton',
    'dip',
    'formula',
    'meatless',
    'nougat',
    'pesto', 'pop', 'porridge',
    'scone', 'strudel',
  },

  Category.VEGETARIAN: {
    'baklava', 'banana split', 'biscuit', 'borscht', 'butter',
    'cake', 'cappuccino', 'caramel', 'chocolate', 'cheese', 'cobbler', 'cookie',
    'cream', 'creme', 'crepe', 'croissant', 'custard',
    'egg',
    'frost', 'french toast', 'fudge',
    'gelato',
    'honey',
    'icing',
    'kefir',
    'latte',
    'macchiato', 'mayonnaise', 'milk', 'mocha', 'mousse', 'mozzarella', 'muffin',
    'paneer', 'pastry', 'pie', 'pizza', 'praline', 'pudding',
    'ranch',
    'tiramisu', 'toffee', 'trifle', 'tzatziki',
    'waffle', 'whey', 'whipped', 'white russian',
    'yogurt',
  },

  Category.VEGAN_OR_OMNI: {
    'jelly',
    'wine',
  },

  Category.VEGAN_VEGETARIAN_OR_OMNI: {
    'dumpling',
    'fat',
    'kimchi',
    'ravioli, ns',
    'sandwich, nfs', 'soup, nfs', 'stew, nfs', 'sushi, nfs',
  },

  Category.VEGETARIAN_OR_OMNI: set(),

  Category.OMNI: {
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
    'moose', 'mortadella', 'mullet', 'mussel',
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

all_tokens = reduce(lambda x, y: x | y, categories_to_tokens.values(), set())

all_tokens_finder = MaxiMunchTokenFinder(all_tokens)

def categorize(description) -> Category:
  names_in_desc = all_tokens_finder.find_all(description.lower())

  contained_token_categories = {
    category for category, tokens in categories_to_tokens.items()
    if any(name in tokens for name in names_in_desc)
  }

  if Category.OMNI in contained_token_categories:
    return Category.OMNI
  if Category.VEGETARIAN_OR_OMNI in contained_token_categories:
    return Category.VEGETARIAN_OR_OMNI
  if Category.VEGAN_VEGETARIAN_OR_OMNI in contained_token_categories:
    if Category.VEGETARIAN in contained_token_categories:
      return Category.VEGETARIAN_OR_OMNI
    return Category.VEGAN_VEGETARIAN_OR_OMNI
  if Category.VEGAN_OR_OMNI in contained_token_categories:
    if Category.VEGETARIAN in contained_token_categories:
      return Category.VEGETARIAN_OR_OMNI
    return Category.VEGAN_OR_OMNI
  if Category.VEGETARIAN in contained_token_categories:
    return Category.VEGETARIAN
  if Category.VEGAN_OR_VEGETARIAN in contained_token_categories:
    return Category.VEGAN_OR_VEGETARIAN
  if Category.VEGETARIAN in contained_token_categories:
    return Category.VEGETARIAN
  if Category.VEGAN in contained_token_categories:
    return Category.VEGAN
  return Category.UNCATEGORIZED

@dataclass(frozen=True)
class Food:
  description: str
  fdc_id: int

  @cached_property
  def category(self):
    return categorize(self.description)

  @classmethod
  def from_fdc_food_dict(cls, d: FoodDataDict):
    description = d["description"]
    fdc_id = d["fdcId"]
    return cls(description=description, fdc_id=fdc_id)

  def as_fdc_like_dict(self, include_description=False):
    return {
      **({
        "description": self.description
      } if include_description else {} ),
      "fdcId": self.fdc_id,
      "vegCategory": self.category.name
    }
