techcable.orderedset
===================

[![github](https://img.shields.io/badge/github-Techcable/orderedset.py-master)](https://github.com/Techcable/orderedset.py)
[![pypi](https://img.shields.io/pypi/v/techcable.orderedset)](https://pypi.org/project/techcable.orderedset/)
![types](https://img.shields.io/pypi/types/techcable.orderedset)]

A simple and efficient `OrderedSet` in pure python. Implements both [`MutableSet`] and [`Sequence`].

[`MutableSet`]: https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSet 
[`Sequence`]: https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence 


## Example Usage
```python
from techcable.orderedset import OrderedSet

# prints {1, 2, 7, 3}
print(OrderedSet([1, 2, 7, 2, 3]))
# Implements all standard set methods, still preserves order
print(OrderedSet.of[1,2]) | OrderedSet([3,2,4]))  # {1,2,3,4}
# OrderedSet.of(1, 2) is shorthand for OrderedSet([1, 2]),
# avoiding an extra pair of brackets
print(OrderedSet.of(1, 2)) # {1, 2}


# Implements `append` method, returning True on success
# and False if the item was a duplicate
oset = OrderedSet()
oset.append(1) # True
oset.append(2) # True
oset.append(1) # False - already in set, did nothing
oset.extend([2,3]) # True - at least one success
oset.append([2,3]) # False - all duplicates
```

Supports [pydantic](pydantic.org) validation & serialization:
```python
import pydantic
from techcable.orderedset import OrderedSet

model = pydantic.TypeAdapter(OrderedSet[int])
# prints OrderedSet.of(1,2,7,8)
print(repr(model.validate_python([1,2,7,8])))
assert model.dump_python(OrderedSet.of(1,2,7,8)) == [1,2,7,8]
```

## Potential Future Features
- Implement `OrderedFrozenSet`
- Consider [acceleration module] using C/Rust/Cython
   - Probably unnecessary since this has library has very little overhead compared to the builtin `set`/`list`

[acceleration module]: https://peps.python.org/pep-0399/

## License
Licensed under either the [Apache 2.0 License](./LICENSE-APACHE.txt) or [MIT License](./LICENSE-MIT.txt) at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this project by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions. 
