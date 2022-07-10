## About

The aim of this project is to provide free and open add-on data for the
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
incorrectly categorized foods that will hopefully become fewer over time. At
some point, I might extend the heuristic to use category data provided by the
USDA in addition to the descriptions, which could improve the accuracy a bit.

A rough estimate for a lower bound on the number of errors in the data is given
by the number of known failures in the [reference
data](https://github.com/v3gtb/fooddata-vegattributes/blob/main/reference_samples.csv)
used for tests, which is currently {{ site.data.stats.failure_percentage }}%.
The real percentage of errors will be larger than that as known failures are
likely to be fixed, with the corresponding lines remaining in the reference
data to serve as regression tests.

## Supported datasets

Attributes are provided for foods in the FNDDS ("Survey") and SR Legacy
datasets. Data for both datasets are provided together in one file as foods are
uniquely identified by their FDC ID and the file size is small anyway. As of
now there are no plans to extend this project to the other FDC datasets, but
who knows.

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

where `CATEGORY` is one of the categories listed in the section below and
`fdcId` corresponds to the field of the same name in the FDC datasets.

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
