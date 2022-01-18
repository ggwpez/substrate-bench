# Performance of Substrate across Rust Profiles

Explains how to *execute*, *visualize* and *compare* the output of the Substrate [benchmarking-cli].  
You will need a rust version that supports the `--profile` option, eg: `nightly-2021-12-03`.

## Running the Benchmarks

1. Clone [Substrate].
2. Modify the `Cargo.toml` and add some `[profile.<name>]` sections. Use this to add compiler and linker flags; [Example](Cargo.toml.sample)
3. Pick some pallets of which you want to run the benchmarks.
4. Call the `bench.py` script with the profiles and pallets.

Example invocation for the profiles `release` and `lto-fat` with pallets `balances` and `lottery`:
```sh
python3 bench.py --profiles release lto-fat --pallets pallet-balances pallet-lottery --cwd ../path-to-substrate-repo
```
This (over)writes one `.txt` file per profile into a `results` folder. Each file contains the timings of all extrinsics of the selected pallets in raw format.  
The options for the benchmark are taken from the [bench-bot].

## Analysis

### Deps
Install the dependencies with:  
```sh
pip install numpy matplotlib more-itertools
```

### Plotting

Use the `plot.py` script to visualize the different timing results.  
Example:
```sh
python3 plot.py $(find raws/wasm-compiled -type f) --grid 3x2
```
Should produce:
![](.imgs/wasm-compiled.png)

<!-- LINKS -->
[Substrate]: https://github.com/paritytech/substrate
[benchmarking-cli]: https://github.com/paritytech/substrate/tree/master/utils/frame/benchmarking-cli
[bench-bot]: https://github.com/paritytech/bench-bot/blob/master/bench.js
