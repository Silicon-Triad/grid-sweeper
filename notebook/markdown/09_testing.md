## 5. Testing and validation

Three test runs (spec §8.2). Each prints the configuration (the input files and the grid),
the schedule with its constraint check, and the integration output for UCS and A\*. Invalid
input is caught and reported (`InputError`), never a crash.
