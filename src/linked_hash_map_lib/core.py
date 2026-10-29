"""Core implementation of :class:`LinkedHashMap`.

Design notes
------------
The map is a doubly-linked list of entries plus a dict mapping keys to
list nodes. This gives O(1) get/set/delete and O(n) ordered iteration.

We deliberately keep the public surface tiny: ``__getitem__``,
``__setitem__``, ``__delitem__``, ``__contains__``, ``__len__``,
``__iter__``, ``__eq__``, :meth:`get`, :meth:`setdefault`,
:meth:`pop`, :meth:`move_to_end`, :meth:`keys`, :meth:`values`,
:meth:`items`, and :meth:`clear`.

No automatic LRU eviction is provided. The caller decides when and
whether to evict; this keeps the data structure honest about what it is
(a map) rather than smuggling in a policy.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Tuple


class _Node:
    """A node in the doubly-linked list backing :class:`LinkedHashMap`.

    Stored as a plain class rather than a dataclass to avoid the import
    overhead (tiny, but real) and to keep attribute access unconditional.
    Nodes are internal; users never see them.
    """

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: Any, value: Any, prev: Any = None, next: Any = None) -> None:
        self.key = key
        self.value = value
        self.prev = prev
        self.next = next


class LinkedHashMap:
    """A hash map preserving insertion order of keys.

    Unlike :class:`dict`, a key can be moved to the end of the iteration
    order after it has been inserted via :meth:`move_to_end`. This is the
    single feature ``dict`` does not offer and the reason this class
    exists.

    Equality compares the ordered sequence of (key, value) pairs, so two
    maps with the same entries in different order are *not* equal. This
    matches the intuition that order is part of the structure's identity.
    """

    __slots__ = ("_map", "_head", "_tail")

    def __init__(self, items: Any = None) -> None:
        # _map maps key -> _Node. We keep a real dict here because hash
        # lookup is exactly what dict is good at; the linked list only
        # carries ordering information dict cannot mutate cheaply.
        object.__setattr__(self, "_map", {})
        # Sentinel head/tail simplifies insert/remove: every real node
        # is bracketed by sentinels, so we never special-case None
        # neighbours. Head.prev and tail.next stay None.
        object.__setattr__(self, "_head", _Node(None, None))
        object.__setattr__(self, "_tail", _Node(None, None))
        self._head.next = self._tail
        self._tail.prev = self._head

        if items is not None:
            # Accept a mapping or an iterable of pairs. We do not call
            # dict(items) because that would silently collapse duplicate
            # keys before we see them; iterating preserves last-wins
            # semantics explicitly and keeps order stable.
            if isinstance(items, dict):
                iterable: Any = items.items()
            else:
                iterable = items
            for key, value in iterable:
                self[key] = value

    # ------------------------------------------------------------------
    # Internal list helpers
    # ------------------------------------------------------------------
    def _append_node(self, node: _Node) -> None:
        """Insert *node* immediately before the tail sentinel."""
        prev = self._tail.prev
        node.prev = prev
        node.next = self._tail
        prev.next = node
        self._tail.prev = node

    def _unlink_node(self, node: _Node) -> None:
        """Remove *node* from the linked list (does not touch _map)."""
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None

    # ------------------------------------------------------------------
    # Mapping protocol
    # ------------------------------------------------------------------
    def __getitem__(self, key: Any) -> Any:
        return self._map[key].value

    def __setitem__(self, key: Any, value: Any) -> None:
        existing = self._map.get(key)
        if existing is None:
            node = _Node(key, value)
            self._map[key] = node
            self._append_node(node)
        else:
            existing.value = value

    def __delitem__(self, key: Any) -> None:
        node = self._map.pop(key)
        self._unlink_node(node)

    def __contains__(self, key: object) -> bool:
        return key in self._map

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self) -> Iterator[Any]:
        node = self._head.next
        while node is not self._tail:
            yield node.key
            node = node.next

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LinkedHashMap):
            return NotImplemented
        return list(self.items()) == list(other.items())

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __repr__(self) -> str:
        pairs = ", ".join(f"{key!r}: {value!r}" for key, value in self.items())
        return f"LinkedHashMap({{{pairs}}})"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def move_to_end(self, key: Any) -> None:
        """Move an existing key to the end of the iteration order.

        Raises :class:`KeyError` if the key is absent. We refuse to
        silently insert because doing so would make a read-like operation
        have a write side effect — a classic source of confusing bugs.
        """
        node = self._map[key]  # raises KeyError if missing
        self._unlink_node(node)
        self._append_node(node)

    def get(self, key: Any, default: Any = None) -> Any:
        node = self._map.get(key)
        if node is None:
            return default
        return node.value

    def setdefault(self, key: Any, default: Any = None) -> Any:
        node = self._map.get(key)
        if node is not None:
            return node.value
        self[key] = default
        return default

    def pop(self, key: Any, *args: Any) -> Any:
        """Remove *key* and return its value.

        With a second argument, return it when *key* is missing instead
        of raising. We accept ``*args`` rather than a keyword ``default``
        to match :meth:`dict.pop` exactly — callers expect that shape.
        """
        if key in self._map:
            node = self._map.pop(key)
            self._unlink_node(node)
            return node.value
        if args:
            return args[0]
        raise KeyError(key)

    def clear(self) -> None:
        self._map.clear()
        self._head.next = self._tail
        self._tail.prev = self._head

    def keys(self) -> List[Any]:
        return list(iter(self))

    def values(self) -> List[Any]:
        return [node.value for node in self._iter_nodes()]

    def items(self) -> List[Tuple[Any, Any]]:
        return [(node.key, node.value) for node in self._iter_nodes()]

    # ------------------------------------------------------------------
    # Internal iteration
    # ------------------------------------------------------------------
    def _iter_nodes(self) -> Iterator[_Node]:
        node = self._head.next
        while node is not self._tail:
            yield node
            node = node.next
