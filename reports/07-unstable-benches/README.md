# Observation

1. The base weight of `Utility::batch` and multiple contract functions are unstable when re-run multiple times.
2. The weight of `StateTrieMigration::migrate_custom_child_success` weight is unstable.
3. Multiple benchmarks exhibited unstable result behaviour when re-run on the same dedicated reference hardware.  

![](observation.png)
![](observation_2.png)

32 of ~550 benchmarks exhibited unstable behaviour with changes of more than +-10%.  
This leads to confusion and delays when transitioning to the new VM runners.  

# Local Investigation

## `migrate_custom_child_success`

Reproducing this issue locally was done by re-running the same benchmark many times with same parameters by using [this](https://github.com/ggwpez/substrate-scripts/blob/master/print-frame-cli-output/frame-cli-multiple.sh) script. Results can be plotted with [this](https://github.com/ggwpez/substrate-scripts/blob/master/print-frame-cli-output/print.py) one.  

The first local testing focused on `migrate_custom_child_success` from pallet `state-trie-migration`. Running it multiple times showed odd behaviour whereas normally the result would settle to 5µs in 90% of the cases, but in the other cases it spiked to ~9µs. Reproducible. It seemed like the benchmark had two stable output states: 5µs and 9µs.  
Plotting two hand-picked results which exhibit this behaviour look like this:

![](local.png)

The two graph are very similar *besides* being offset by about 4µs. Since this measurement resulted in a ~9µs result.

Running with more repeats shows the same behaviour.  

`i9` 20 Reps | `i9` 200 Reps
:-:|:-:
![](migrate-local-20.png) | ![](migrate-local-200.png)

For some reason a few runs show very persistent increased timings. This is from my local PC (i9-13900K). My assumption that this is caused by the efficiency cores of the `i9` seems to hold. Lets see what happens when we disable any efficiency cores:

`i9 (Efficiency cores disabled) 20 Reps` | `i9 (Efficiency cores disabled)` 200 Reps
:-:|:-:
![](migrate-local-20-no-effi.png) | ![](migrate-local-200-no-effi.png)

And now by disabling all possible performance cores. CPU zero cannot be disabled and seems to do the main workload here, since there are still mostly fast runs but definitely more slow ones than before.

`i9 (Performance cores disabled) 20 Reps` | `i9 (Performance cores disabled)` 200 Reps
:-:|:-:
![](migrate-local-20-no-perf.png) | ![](migrate-local-200-no-perf.png)

The whole thing becomes even more apparent when forcing it to schedule on efficiency cores with `taskset -c 16-32`.

`i9 (Only efficiency cores) 20 Reps` | `i9 (Only efficiency cores)` 200 Reps
:-:|:-:
![](migrate-local-20-only-effi.png) | ![](migrate-local-200-only-effi.png)

The grouping this time is tightly around ~9µs. Therefore my local variations between the results can be explained by whether the task was scheduled to run on an efficiency or performance thread.

On the new VM runners this does not occur. There are outliers, but they are not persistent. Note that this is log-scale and looks worse than it is.

`vm` 20 Reps | `vm` 200 Reps
:-:|:-:
![](migrate-vm-20.png) | ![](migrate-vm-200.png)

Just for comparison also trying this on the old ref hardware `bm2` server (i7-7700K):  

`bm2` 20 Reps | `bm2` 200 Reps
:-:|:-:
![](migrate-bm2-20.png) | ![](migrate-bm2-200.png)

## `batch`

Next up looking at `batch` of `pallet-utility` locally on my PC:  

`i9` 20 Reps | `i9` 200 Reps
:-:|:-:
![](batch-20-local.png)  |  ![](batch-200-local.png)

Looks very linear with the occasional outlier. Running the same on the new VM reference hardware actually shows even better graphs:  

`vm` 20 Reps | `vm` 200 Reps
:-:|:-:
![](batch-20-vm.png)  |  ![](batch-200-vm.png)

And for comparison `bm2`, also very linear:

`bm2` 20 Reps | `bm2` 200 Reps
:-:|:-:
![](batch-20-bm2.png)  |  ![](batch-200-bm2.png)

The y-axis offset of the linear fittings calculated by FRAME for these results vary a lot while the component stays much the same. To demonstrate that the base weight (y axis offset) in this case does not matter, here are two linear equations with the same component but once for base weight 0 and the other for 30.  

`vm` 20 Reps | `vm` 200 Reps
:-:|:-:
![](batch-20-vm-fittings.png)  |  ![](batch-200-vm-fittings.png)

It can be seen that the calculated linear fitting is very good in both cases, no matter whether the base weight fluctuates by 30 µs or not.

Further analysis of the last 10 master commits at around `435446fe0` did not show any abnormal behaviour either.  

`bm2 (Last 10 commits)` 20 Reps | `bm2 (Last 10 commits)` 200 Reps
:-:|:-:
![](bm2-master-10-batch-20.png)  |  ![](bm2-master-10-batch-200.png)

The linear fitting groups are strongest around 4-4.3 and spike up to 4.7 for 20 reps and 4.6 for 200 reps.  
I therefore conclude that the `Utility::batch` benchmark is *stable* and the variance in weight only comes from fluctuating base-weight calculation. Note that in this case there is no base weight and therefore the linear fitting will report different (invalid) values in the range of -110 - 35µs.
