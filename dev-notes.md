# Development notes

Notes only relevant for myself in 3 years or anyone else who looks at the code.

## Apologies

It turned out needlessly messy, in particular because

a) I tried to use it as a "testbed" for some techniques (e.g. there is a lot of
   dependency inversion in certain parts) and
b) I tried to go for zero dependencies for the package itself (i.e. excluding
   development/testing tools like pytest). No real reason why.

## "Indexed Jsonable Store"

As a consequence of (b) above, I wrote a  document database-like thing (with
greatly reduced functionality however) under `utils/indexed_jsonable_store`.
The goal here was to have a compressed and randomly accessible database of JSON
FoodData entries so that e.g. tests run faster than they would if the entire
original FoodData JSON had to be read in each time, without blowing up my hard
drive with a huge uncompressed SQLite database or anything like that. Had I
been fine with dependencies, I could've used one of the existing document
databases offering compression instead.

## TODO

More to follow at some point...
