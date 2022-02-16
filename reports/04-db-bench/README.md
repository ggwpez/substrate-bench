# DB access speed

This report focuses only on `RocksDb` and `ParityDb` without any Storage trie overhead.  

# Observations

## 32k bump in ParityDB

There is a bump at 2^15 with a nearly 50% increase for ParityDB.
The black lies are at `i * 4096 + 32768`.

![](jump%20at%2032k.png)
