# Re-benchmark everything with rust flags

The idea is to enable rust compiler optimizations to get lower weights.  
It was brought up in [polkadot/#4311](https://github.com/paritytech/polkadot/issues/4311) and was done before in [moonbeam/#967](https://github.com/PureStake/moonbeam/pull/967). 
The Substrate tracking issue is [substrate/#10608](https://github.com/paritytech/substrate/issues/10608).

# Setup

Very simple; enable optimization flags and re-run all benchmarks.

1. Clone the [Substrate repo](https://github.com/paritytech/substrate).
2. Append a new *profile* to the `Cargo.toml`. You can use the [Cargo.toml.sample](Cargo.toml.sample) for your convenience.
3. Execute the [run.py](run.py) script with your newly added *profile*:
	```sh
	python3 run.py --profile optimized --skip pallet_offences pallet_mmr pallet_babe pallet_grandpa --cwd ../path-to-substrate
	```
	**Note** Expect for `offences` ([#10027](https://github.com/paritytech/substrate/issues/10027)), the `--skip`ed pallets do not have `weight.rs` files. They have `default_weights.rs` instead and need to ne addressed manually.
4. You should be seeing something like this:
   ```pre
	2022-01-18 13:00:48: Compiling ...
	2022-01-18 13:00:48: Listing ...
	2022-01-18 13:00:50: Running 402 cases across 35 pallets. Skipping 4 pallets.
	2022-01-18 13:00:50: [1/35] frame_benchmarking: 8 cases ...
	...
	2022-01-18 13:04:35: [35/35] pallet_vesting: 8 cases ...
	2022-01-18 13:04:37: 🎉 Raws written to 'raw-optimized', weights to 'weights-optimized'
	2022-01-18 13:04:37: You can enact the new weights with
	cp -RT weights-optimized/frame ./frame
   ```
5. Inspect the weights in `weights-optimized/frame`. They are written to a different directory per default to allow it to re-run without re-compile. You can then copy them over with the command logged above.
The raw files in `raw-optimized` offer advanced introspection.
1. Nice, you now have lower weights!
