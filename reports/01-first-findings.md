I tested multiple compiler flags to see if we get increased benchmarking performance.

Below you can see the outcome of the first experiments for the `balances` pallet.  
This should just show what *can* be done, since it is by no means exhaustive.  

Look out for the `BASELINE` graph which is the current `release` configuration
and compare it with the other ones.  
As you can see; the `BASELINE` is outperformed by every optimisation.  
The only downside is the increased compilation time.  

![](../out.png)
(The bin size is not uniform in the graph, but you get the idea.)

Legend:  
- baseline: Current `release` configuration as reference.
- lto-fat: [Link time optimization](https://doc.rust-lang.org/rustc/linker-plugin-lto.html) with argument `fat`.
- lto-thin: [Link time optimization](https://doc.rust-lang.org/rustc/linker-plugin-lto.html) with argument `thin`.
- cg-1: [Codegen-units](https://doc.rust-lang.org/rustc/codegen-options/index.html#codegen-units) set to one.
- cpu-target: [target-cpu](https://doc.rust-lang.org/rustc/codegen-options/index.html#target-cpu) set to "native". This does not influence the `wasm=compiled` option.

Rust pros please DM me if you have ideas for other flags and tweaks.
