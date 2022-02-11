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

First formula: const for < 10k and 

# Open Qs:
- What is the grouping at 30k?
- from Shawn: parity db is like noticeably better for 0 to 10,000 and noticeably worse for 10,000 + 
