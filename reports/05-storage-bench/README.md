# Storage Access Benchmarking

The weights for storage Read/Write are currently hard-coded [here]. This is inflexible and possibly outdated.  
I started investigating storage access for *RocksDB* and *ParityDB* on *Kusama* in different configurations.

The results were not created on reference hardware and just for relative comparison.

## Kusama - Read: RocksDB and ParityDB

| | |
|-|-|
| ![](ksm_11329492_rocks.png) | ![](ksm_11343839_parity.png) |

## Comparision

![](both.png)

[here]: https://github.com/paritytech/substrate/blob/ded44948e2d5a398abcb4e342b0513cb690961bb/frame/support/src/weights.rs

# Observation

Below 10k the weight is nearly constant and above that it seems to scale linear with the size.  
Let's find the cutoff and a simple formula.  

## Guessed values
Now trying to find a model that is very fast to compute but has good accuracy.  
First try thanks to @shawntabrizi:  
```rust
if s < CUTOFF:
	CHEAP
else:
	CHEAP + (s - CUTOFF) * SLOPE
```

with `CUTOFF = 10k`, `CHEAP = 80` and `SLOPE = 1/1000`:

![](simple_model.png)

## Statistics...

Trying to find some good approximation slopes. This uses the values <10Kb as to calculate a offset for the slope by using its 99% percentile.  
Seems to work fine for RocksDB but not for ParityDB because of the bump described in [report 04].  


| | |
|-|-|
| ![](rocks%20formula.png) | ![](parity%20formula.png) |


# Open Qs:
## What is the grouping at 30k?
Must be 35k-36k.

## Redo with Polkadot data instead of Kusama

## from Shawn: parity db is like noticeably better for 0 to 10,000 and noticeably worse for 10,000 + 
There is a bump at 32k for ParityDB, see [report 04].


[report 04]: ../04-db-bench/README.md
