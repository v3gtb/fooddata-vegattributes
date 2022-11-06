# fooddata-vegattributes
[USDA's FDC FoodData datasets](https://fdc.nal.usda.gov/download-datasets.html)
containing attributes that categorize foods as vegan, vegetarian, or neither.

This will hopefully enable applications and services that deal with nutrition
data to take these dietary preferences into account, e.g. when displaying or
suggesting foods to users. The target audience of this project are mainly small
open source projects, although nothing keeps you from using it in a commercial
project (see the License section below).

## Accuracy

The data are generated using a naive heuristic based only on the descriptions
of each food and those of its ingredients, which are compared to hardcoded
lists of phrases and the most likely categories they suggest. Neither this
approach nor the lists of phrases are perfect, so there are still many
incorrectly categorized foods that will hopefully become fewer over time.

A rough estimate for a lower bound on the percentage of errors is the
percentage of known failures in the [reference
data](https://github.com/v3gtb/fooddata-vegattributes/blob/main/reference_samples.csv),
which is currently 4.7%.
The real percentage of errors will be larger than that as known failures are
likely to be fixed, after which the lines in question remain in the reference
data with the known failure mark removed to serve as regression tests.

Note that categories listed in the reference data override those determined by
the heuristic in the final exported data, so any individual known failure
listed there has already been corrected.

If you find any mistakes, feel free to
[open an issue](https://github.com/v3gtb/fooddata-vegattributes/issues/new).

## Strictness

For those foods whose categorization as vegan/vegetarian/omni depends on one's
level of "strictness", an attempt is made to classify them as an appropriate
composite category. E.g., wines should ideally all be categorized as
`VEGAN_VEGETARIAN_OR_OMNI` because [certain filtration methods normally used in
the winemaking process involve animal
products](https://www.peta.org/about-peta/faq/is-wine-vegan/), some of which
require killing the animal to extract, although it's plausible that a subset of
vegans/vegetarians would consider them vegan/vegetarian regardless.

Note that these same composite categories are also used more generally in cases
in which it's impossible to tell from the available information whether
something is vegan/vegetarian or not. Although this meaning is technically
distinct from the strictness-dependent categorization above, in practice they
tend to overlap almost perfectly. Returning e.g. to the example above, there do
exist strictly vegan wines made without resorting to animal products in any
step of the process, but a description saying just "wine" could refer to either
these or the non-vegan variants.

## Supported datasets

Attributes are provided for foods in the FNDDS ("Survey") and SR Legacy
datasets. Data for both datasets are provided together in one file as foods are
uniquely identified by e.g. their FDC ID and the file size is small anyway. As
of now there are no plans to extend this project to the other FDC datasets, but
who knows.

## Download and file format

The latest generated dataset can be found on the [GitHub releases
page](https://github.com/v3gtb/fooddata-vegattributes/releases).

It is shipped as a JSON file containing a list of entries of the form

```json
{
  "fdcId": 123,
  "vegCategory": "CATEGORY",
  "description": "USDA FDC description/name of the food",
  # either:
  "foodCode": 456,
  # or:
  "ndbNumber": 789
}
```

where `CATEGORY` is one of the categories listed in the section below and
`fdcId`, `foodCode`, `ndbNumber` and `description` correspond to the fields of
the same names in the FDC datasets. `foodCode` only appears in the FNDDS data
and `ndbNumber` only in the SR Legacy data, so which one of these will be
present in a given entry depends on which dataset the food entry came from.
The `description` is only included as a debugging help - the proper way to find
it or any other properties of a given food is to perform a lookup in the FDC
datasets by the given IDs.

The FDC ID by itself is enough to uniquely identify foods, but it is my
understanding that a new FDC ID is assigned to "the same" food on every release
of a FDC dataset, while IDs like the Food Code and NDB Number remain the same,
the idea being that the FDC ID identifies not just a food but also the specific
properties (e.g. determined nutrients) associated with it in that release.
So for easier cross-FDC-release compatibility, Food Code or NDB Number are
included here as well. Note, however, that I'm not sure whether e.g. the
ingredient list or description can be updated as well between releases, which
would have the potential to change the categorization as determined by this
project. In that case, it might be more correct to use only on the FDC ID,
although the number of errors caused by updated descriptions or ingredients is
expected to be much, much lower than that caused by failures of the heuristic.

## Web preview

For debugging and demoing purposes, the current lists of foods in each category
can be viewed here:

- [VEGAN](https://v3gtb.github.io/fooddata-vegattributes/category-lists/vegan) (4250 entries)
- [VEGAN_OR_VEGETARIAN](https://v3gtb.github.io/fooddata-vegattributes/category-lists/vegan-or-vegetarian) (569 entries)
- [VEGETARIAN](https://v3gtb.github.io/fooddata-vegattributes/category-lists/vegetarian) (3281 entries)
- [VEGAN_OR_OMNI](https://v3gtb.github.io/fooddata-vegattributes/category-lists/vegan-or-omni) (4 entries)
- [VEGAN_VEGETARIAN_OR_OMNI](https://v3gtb.github.io/fooddata-vegattributes/category-lists/vegan-vegetarian-or-omni) (238 entries)
- [VEGETARIAN_OR_OMNI](https://v3gtb.github.io/fooddata-vegattributes/category-lists/vegetarian-or-omni) (96 entries)
- [OMNI](https://v3gtb.github.io/fooddata-vegattributes/category-lists/omni) (6104 entries)
- [UNCATEGORIZED](https://v3gtb.github.io/fooddata-vegattributes/category-lists/uncategorized) (334 entries)


## Source code and development

The script used to generate the data released by this project from FDC data via
the heuristic explained above can be found in the project's
[GitHub repository](https://github.com/v3gtb/fooddata-vegattributes).

Some incomplete notes on development can be found [here](https://v3gtb.github.io/fooddata-vegattributes/dev-notes.html).

## License

Like the USDA FDC datasets themselves, the data published by this project is
hereby released into the public domain or, in jurisdictions where this is not
possible, the closest legal equivalent.

The script to generate the data is provided under the MIT license.
