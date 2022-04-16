from dataclasses import dataclass
from enum import Enum
from functools import cached_property
import json
from tabulate import tabulate
from textwrap import dedent
import random
import re

class Estimation(Enum):
  ALMOST_DEFINITELY = "ALMOST_DEFINITELY"
  COULD_BE_EITHER = "COULD_BE_EITHER"
  ALMOST_DEFINITELY_NOT = "ALMOST_DEFINITELY_NOT"
  UNCATEGORIZED = "UNCATEGORIZED"

  def __bool__(self):
    return self == self.ALMOST_DEFINITELY


vegan_tokens = {
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
  'grain', 'grape', 'greens', 'guava', 'gum',
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
}

non_vegan_tokens = {
  'adobo', 'anchovy', 'animal',
  'bacon', 'baklava', 'banana split', 'barracuda', 'bass',
  'bear', 'beaver', 'beef',
  'biscuit', 'bison', 'bologna', 'borscht', 'brain', 'burger', 'butter',
  'cake', 'cappuccino', 'caramel', 'caribou', 'carp', 'casserole',
  'chicken', 'chocolate', 'chorizo', 'cheese',
  'clam', 'cobbler', 'cod', 'cookie',
  'crab', 'cream', 'creme', 'crepe', 'croaker', 'croissant', 'custard',
  'deer', 'dog', 'dove', 'duck',
  'egg', 'eel',
  'fish', 'frost', 'flounder', 'french toast', 'frog', 'fudge',
  'gelatin', 'gelato', 'gizzard', 'goat', 'goulash', 'gravy', 'ground hog',
  'haddock', 'halibut', 'herring', 'ham', 'honey',
  'icing',
  'jerky',
  'kefir', 'kidney',
  'lamb', 'latte', 'lard', 'liver', 'lobster',
  'macchiato', 'mackerel', 'marshmallow', 'matzo', 'mayonnaise',
  'meat', 'meringue', 'milk',
  'mocha', 'moose', 'mortadella', 'mousse', 'mozzarella',
  'muffin', 'mullet', 'mussel',
  'nacho',
  'octopus', 'okra', 'opossum', 'ostrich', 'oyster', 'ox',
  'pad thai', 'pastrami', 'pastry', 'pepperoni', 'pepperpot', 'perch',
  'pie', 'pig', 'pike', 'pizza', 'pheasant',
  'porgy', 'pork', 'pot roast', 'potato skins', 'praline', 'pudding',
  'quail',
  'rabbit', 'raccoon', 'ranch', 'ray', 'roe',
  'salami', 'salmon', 'sardine', 'sausage', 'scallop', 'seafood',
  'shark', 'shrimp', 'snail', 'souffle', 'squid', 'squirrel',
  'steak', 'sturgeon',
  'thuringer', 'tilapia', 'tiramisu',
  'toffee', 'tongue', 'trifle', 'tripe', 'trout',
  'tuna', 'turkey', 'turtle', 'tzatziki',
  'veal', 'venison',
  'waffle', 'whey', 'whipped', 'white russian', 'wurst',
  'yogurt'
}

could_be_either_tokens = {
  'bar',
  'candy, nfs', 'chutney', 'cocktail, nfs', 'cracker', 'crouton',
  'dip',
  'dumpling',
  'fat, nfs',
  'formula',
  'jelly',
  'kimchi',
  'nougat',
  'pesto',
  'pop',
  'porridge',
  'ravioli, ns',
  'scone', 'strudel',
  'sandwich, nfs',
  'soup, nfs',
  'stew, nfs',
  'sushi, nfs',
  'wine',
}


all_tokens = vegan_tokens | non_vegan_tokens | could_be_either_tokens


class MaxiMunchTokenFinder:
  def __init__(self, tokens):
    self.regex = re.compile(
      "("
      +
      "|".join(
        re.escape(token) for token in sorted(tokens, key=len, reverse=True)
      )
      +
      ")"
    )

  def find_all(self, s: str):
    return self.regex.findall(s)


all_tokens_finder = MaxiMunchTokenFinder(all_tokens)


def sounds_vegan(description) -> Estimation:
  names_in_desc = all_tokens_finder.find_all(description.lower())

  contains_vegan_tokens = any(
    name in vegan_tokens for name in names_in_desc
  )
  contains_non_vegan_tokens = any(
    name in non_vegan_tokens for name in names_in_desc
  )
  contains_could_be_either_tokens = any(
    name in could_be_either_tokens for name in names_in_desc
  )

  if contains_non_vegan_tokens:
    return Estimation.ALMOST_DEFINITELY_NOT
  elif contains_could_be_either_tokens:
    return Estimation.COULD_BE_EITHER
  elif contains_vegan_tokens:
    return Estimation.ALMOST_DEFINITELY
  return Estimation.UNCATEGORIZED

@dataclass(frozen=True)
class Food:
  description: str

  @cached_property
  def sounds_vegan(self):
    return sounds_vegan(self.description)


def select_n_random(items, n, criterion=None):
  from tqdm import tqdm
  t = tqdm()
  indices_todo = list(range(len(items)))
  selected = []
  while len(selected) < n:
    t.update()
    if not indices_todo:
      if criterion is not None:
        error_msg = (
          "not enough items fulfilling criterion in given sequence"
          if criterion is not None else "not enough items in given sequence"
        )
      raise ValueError(error_msg)
    i = random.choice(indices_todo)
    indices_todo.remove(i)
    item = items[i]
    if criterion is not None and not criterion(item):
      continue
    else:
      selected.append(item)
  return selected


def main():
  with open("FoodData_Central_survey_food_json_2021-10-28.json") as f:
    d = json.load(f)

  food_ds = d["SurveyFoods"]
  foods = []

  for food_d in food_ds:
    description = food_d["description"]
    food = Food(description=description)
    foods.append(food)

  # go through all foods and assign categories
  vegan_foods = []
  uncategorized_foods = []
  could_be_either_foods = []
  non_vegan_foods = []
  for food in foods:
    if food.sounds_vegan == Estimation.ALMOST_DEFINITELY:
      vegan_foods.append(food)
    elif food.sounds_vegan == Estimation.COULD_BE_EITHER:
      could_be_either_foods.append(food)
    elif food.sounds_vegan == Estimation.ALMOST_DEFINITELY_NOT:
      non_vegan_foods.append(food)
    elif food.sounds_vegan == Estimation.UNCATEGORIZED:
      uncategorized_foods.append(food)

  # stats
  print(dedent(f"""\
  numbers:
  {len(vegan_foods)} vegan.
  {len(non_vegan_foods)} non-vegan.
  {len(could_be_either_foods)} could be either.
  {len(uncategorized_foods)} uncategorized.
  """).strip())

  n_samples = 100
  vegan_sample = select_n_random(vegan_foods, n_samples)
  could_be_either_sample = select_n_random(could_be_either_foods, n_samples)
  non_vegan_sample = select_n_random(non_vegan_foods, n_samples)
  uncategorized_sample = select_n_random(uncategorized_foods, n_samples)

  print(tabulate([
    [vf.description[:30], uf.description[:30], cbef.description[:30], nvf.description[:30]]
    for vf, uf, cbef, nvf in zip(vegan_sample, uncategorized_sample, could_be_either_sample, non_vegan_sample)
  ]))


if __name__ == "__main__":
  main()
