techcable.orderedset
===================

[![github](https://img.shields.io/badge/github-Techcable/orderedset.py-master)](https://github.com/Techcable/orderedset.py)
[![pypi](https://img.shields.io/pypi/v/techcable.orderedset)](https://pypi.org/project/techcable.orderedset/)
![types](https://img.shields.io/pypi/types/techcable.orderedset)]

A simple and efficient pure-python ordered set.

## Example Usage
```python
from techcable.orderedset import OrderedSet

# prints {1, 2, 7, 3}
print(OrderedSet([1, 2, 7, 2, 3]))
```

Supports [pydantic](pydantic.org) validation & serialization:
```python
import pydantic
from techcable.orderedset import OrderedSet

model = pydantic.TypeAdapter(OrderedSet[int])
# prints OrderedSet([1,2,7,8])
print(repr(model.validate_python([1,2,7,8])))
assert model.dump_python(OrderedSet([1,2,7,8])) == [1,2,7,8]
```

## Potential Future Features
- Add [acceleration module] using C/Rust/Cython
- Implemented `OrderedFrozenSet`
- Publish HTML documentation using Sphinx or [pdoc](https://pdoc.dev/)

[acceleration module]: https://peps.python.org/pep-0399/

## License
Licensed under either the [Apache 2.0 License](./LICENSE-APACHE.txt) or [MIT License](./LICENSE-MIT.txt) at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in Serde by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions. 
