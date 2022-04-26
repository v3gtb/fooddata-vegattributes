## About

The aim of this project is to provide free (as in freedom) add-on data for the
[USDA's FDC FoodData datasets](https://fdc.nal.usda.gov/download-datasets.html)
containing attributes that categorize foods as vegan, vegetarian, or neither.

This will hopefully enable applications and services that deal with nutrition
data to take these dietary preferences into account, e.g. when displaying or
suggesting foods to users. The target audience of this project are mainly small
open source projects, although nothing keeps you from using it in a commercial
project (see the License section below).

## Accuracy

The data are generated using a naive heuristic based only on the description of
each food, which is compared to a hardcoded list of phrases and the most likely
categories they suggest. Neither this approach nor the list of phrases are
perfect, so there are still many incorrectly categorized foods that will
hopefully become fewer over time. I plan to eventually extend the heuristic to
use ingredient and category data provided by the USDA, which should greatly
improve the accuracy.

## Supported datasets

Attributes are provided for foods in the FNDDS ("Survey") dataset only. As of
now there are no plans to extend this to the other datasets, but who knows.

## Download and file format

The latest generated dataset can be found on the [GitHub releases
page](https://github.com/v3gtb/fooddata-vegattributes/releases).

It is shipped as a JSON file containing a list of entries of the form

```json
{
  "fdcId": "some-fdc-id",
  "vegCategory": "CATEGORY"
}
```

where `CATEGORY` is one of the categories listed in the section below.

The script used to generate this data via the aforementioned heuristic can be
found in the [GitHub
repository](https://github.com/v3gtb/fooddata-vegattributes).

## Web preview

For debugging and demoing purposes, the current lists of foods and their FDC
IDs for each category can be viewed here:

{% include_relative categories-toc.md %}

## License

Like the USDA FDC datasets themselves, the data published by this project is
hereby released into the public domain or, in jurisdiction where this is not
possible, the closest legal equivalent.

The script to generate the data is provided under the MIT license.
