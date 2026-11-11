# linked_hash_map_lib

A small, dependency-free hash map that preserves key insertion order and supports moving an existing key to the end of that order — useful for access-order iteration (e.g. building an LRU cache on top).

```python
from linked_hash_map_lib import LinkedHashMap

m = LinkedHashMap()
m["a"] = 1
m["b"] = 2
m["c"] = 3
m.move_to_end("a")        # iteration order is now [b, c, a]
print(list(m.items()))     # [('b', 2), ('c', 3), ('a', 1)]
```

## Why

Python's `dict` preserves insertion order but offers no way to relocate an existing key within that order. When you need access-order semantics — where touching a key promotes it to the most-recently-used position — `dict` alone is not enough and `collections.OrderedDict`'s `move_to_end` is the canonical solution.

This library provides the same capability in a minimal, self-contained class with an explicit, small surface. It is not a reimplementation of `OrderedDict`'s full API; it covers the common case (get, set, delete, ordered iteration, `move_to_end`) and stops there.

## Design decisions

- **Equality is order-sensitive.** Two `LinkedHashMap` instances are equal only if they contain the same key-value pairs *in the same order*. Order is part of the structure's identity; treating it as irrelevant would be surprising.
- **`move_to_end` raises `KeyError` for absent keys.** It does not insert. Making a read-positioning operation silently write would be a source of bugs.
- **No built-in eviction policy.** The map grows without bound. Callers decide when and whether to evict; this keeps the structure a map rather than smuggling in LRU semantics.

## Edge cases

- Updating an existing key's value preserves its current position in iteration order.
- Constructing from an iterable of pairs applies last-wins semantics for duplicate keys, matching `dict`.
- `pop` accepts a positional default (matching `dict.pop`) and returns it instead of raising when the key is absent.

## Exported names

- `LinkedHashMap` — the only public class, re-exported from the package root.

## Running tests

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

