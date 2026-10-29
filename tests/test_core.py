"""Unit tests for :class:`linked_hash_map_lib.core.LinkedHashMap`.

Tests are written to match the documented behaviour precisely. They do
not exercise methods the class does not implement.
"""

import unittest

from linked_hash_map_lib.core import LinkedHashMap


class TestConstruction(unittest.TestCase):
    def test_empty_construction(self):
        m = LinkedHashMap()
        self.assertEqual(len(m), 0)
        self.assertEqual(list(m), [])

    def test_construct_from_pairs(self):
        m = LinkedHashMap([("a", 1), ("b", 2)])
        self.assertEqual(list(m.items()), [("a", 1), ("b", 2)])

    def test_construct_from_dict(self):
        m = LinkedHashMap({"x": 10, "y": 20})
        self.assertEqual(set(m.items()), {("x", 10), ("y", 20)})


class TestBasicMapping(unittest.TestCase):
    def test_set_get(self):
        m = LinkedHashMap()
        m["a"] = 1
        self.assertEqual(m["a"], 1)

    def test_update_existing_key_preserves_position(self):
        m = LinkedHashMap()
        m["a"] = 1
        m["b"] = 2
        m["a"] = 99
        self.assertEqual(list(m.items()), [("a", 99), ("b", 2)])

    def test_delete(self):
        m = LinkedHashMap([("a", 1), ("b", 2), ("c", 3)])
        del m["b"]
        self.assertEqual(list(m.items()), [("a", 1), ("c", 3)])
        self.assertNotIn("b", m)

    def test_len(self):
        m = LinkedHashMap([("a", 1), ("b", 2)])
        self.assertEqual(len(m), 2)

    def test_contains(self):
        m = LinkedHashMap([("a", 1)])
        self.assertIn("a", m)
        self.assertNotIn("z", m)


class TestOrdering(unittest.TestCase):
    def test_insertion_order_preserved(self):
        m = LinkedHashMap()
        for k in ["c", "a", "b"]:
            m[k] = k.upper()
        self.assertEqual(list(m), ["c", "a", "b"])

    def test_move_to_end(self):
        m = LinkedHashMap([("a", 1), ("b", 2), ("c", 3)])
        m.move_to_end("a")
        self.assertEqual(list(m), ["b", "c", "a"])

    def test_move_to_end_single_element(self):
        m = LinkedHashMap([("only", 1)])
        m.move_to_end("only")
        self.assertEqual(list(m), ["only"])

    def test_move_to_end_missing_raises(self):
        m = LinkedHashMap([("a", 1)])
        with self.assertRaises(KeyError):
            m.move_to_end("missing")


class TestGetSetdefaultPop(unittest.TestCase):
    def test_get_existing(self):
        m = LinkedHashMap([("a", 1)])
        self.assertEqual(m.get("a"), 1)

    def test_get_missing_default(self):
        m = LinkedHashMap()
        self.assertIsNone(m.get("missing"))
        self.assertEqual(m.get("missing", 42), 42)

    def test_setdefault_existing(self):
        m = LinkedHashMap([("a", 1)])
        self.assertEqual(m.setdefault("a", 99), 1)
        self.assertEqual(m["a"], 1)

    def test_setdefault_missing(self):
        m = LinkedHashMap()
        self.assertEqual(m.setdefault("a", 1), 1)
        self.assertEqual(m["a"], 1)

    def test_pop_existing(self):
        m = LinkedHashMap([("a", 1), ("b", 2)])
        self.assertEqual(m.pop("a"), 1)
        self.assertEqual(list(m), ["b"])

    def test_pop_missing_with_default(self):
        m = LinkedHashMap()
        self.assertEqual(m.pop("missing", None), None)

    def test_pop_missing_raises(self):
        m = LinkedHashMap()
        with self.assertRaises(KeyError):
            m.pop("missing")


class TestEqualityAndRepr(unittest.TestCase):
    def test_eq_same_order(self):
        a = LinkedHashMap([("a", 1), ("b", 2)])
        b = LinkedHashMap([("a", 1), ("b", 2)])
        self.assertEqual(a, b)

    def test_eq_different_order_not_equal(self):
        a = LinkedHashMap([("a", 1), ("b", 2)])
        b = LinkedHashMap([("b", 2), ("a", 1)])
        self.assertNotEqual(a, b)

    def test_eq_different_values(self):
        a = LinkedHashMap([("a", 1)])
        b = LinkedHashMap([("a", 2)])
        self.assertNotEqual(a, b)

    def test_eq_non_linkedhashmap(self):
        m = LinkedHashMap([("a", 1)])
        self.assertNotEqual(m, [("a", 1)])

    def test_repr(self):
        m = LinkedHashMap([("a", 1)])
        self.assertEqual(repr(m), "LinkedHashMap({'a': 1})")


class TestClearAndViews(unittest.TestCase):
    def test_clear(self):
        m = LinkedHashMap([("a", 1), ("b", 2)])
        m.clear()
        self.assertEqual(len(m), 0)
        self.assertEqual(list(m), [])

    def test_keys_values_items(self):
        m = LinkedHashMap([("a", 1), ("b", 2)])
        self.assertEqual(m.keys(), ["a", "b"])
        self.assertEqual(m.values(), [1, 2])
        self.assertEqual(m.items(), [("a", 1), ("b", 2)])


if __name__ == "__main__":
    unittest.main()
