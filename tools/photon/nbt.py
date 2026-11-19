"""Minimal, dependency-free big-endian NBT reader/writer for Photon FX files.

Why this exists (see docs/vfx-and-cinematics/PHOTON_FX_FORMAT.md section 1): Photon's three
containers are plain NBT underneath -- ``.fx`` is gzipped, ``.fxproj`` is not,
``.fxpack`` is a zip of gzipped ``.fx`` entries. Nothing here is Minecraft- or
Photon-specific; it is a general NBT codec. ``fx.py`` builds the Photon-shaped
tree on top of it, ``pack.py`` handles the container wrapping.

Design notes
------------
Plain Python ints/floats/strings/dicts/lists cannot round-trip NBT faithfully:
NBT distinguishes Byte/Short/Int/Long (all "just an int" in Python) and
Float/Double (both "just a float"), and a `TAG_List` carries an explicit
element-type byte that must survive even when the list is empty. The spec's
byte-verified files rely on exactly this: ``shape.rotation[i]`` is a Byte-vs-
Int-vs-Float coin flip depending on which file wrote it, and an empty NBT list
(``_childrenId``, disabled ``bursts.payload``) serializes with its element type
byte set to ``TAG_End`` (0), not to whatever type would have gone there.

So every NBT value in this module is a distinct Python type (Byte, Short,
Int, Long, Float, Double, ByteArray, String, List, Compound, IntArray,
LongArray) that remembers its own tag id. A plain ``int``/``float``/``str``/
``dict``/``list`` passed where a tagged value is expected is almost always a
writer bug -- catch it (this module raises TypeError) rather than silently
guessing a tag.

Byte order: NBT is big-endian throughout, including UTF-8 string length
prefixes (unsigned short) and list/array lengths (signed int).
"""

from __future__ import annotations

import gzip
import os
import struct
from typing import Any, Iterable, List as PyList, Optional, Tuple

# --- Tag id constants (photon:fx uses the vanilla NBT tag set only) --------

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12

_TAG_NAMES = {
    TAG_END: "TAG_End",
    TAG_BYTE: "TAG_Byte",
    TAG_SHORT: "TAG_Short",
    TAG_INT: "TAG_Int",
    TAG_LONG: "TAG_Long",
    TAG_FLOAT: "TAG_Float",
    TAG_DOUBLE: "TAG_Double",
    TAG_BYTE_ARRAY: "TAG_Byte_Array",
    TAG_STRING: "TAG_String",
    TAG_LIST: "TAG_List",
    TAG_COMPOUND: "TAG_Compound",
    TAG_INT_ARRAY: "TAG_Int_Array",
    TAG_LONG_ARRAY: "TAG_Long_Array",
}


class NBTError(Exception):
    """Raised on malformed NBT bytes or an invalid tree passed to the writer."""


# --- Tagged value wrapper types ---------------------------------------------
#
# Each wraps a native Python value but carries `tag_id` so the writer never
# has to guess. Numeric wrappers subclass int/float so ordinary arithmetic
# and comparisons on parsed values still work (e.g. `if obj["_enable"]:`).


class Byte(int):
    tag_id = TAG_BYTE

    def __new__(cls, value: int = 0):
        v = int(value) & 0xFF
        if v >= 0x80:
            v -= 0x100
        return int.__new__(cls, v)


class Short(int):
    tag_id = TAG_SHORT

    def __new__(cls, value: int = 0):
        v = int(value) & 0xFFFF
        if v >= 0x8000:
            v -= 0x10000
        return int.__new__(cls, v)


class Int(int):
    tag_id = TAG_INT

    def __new__(cls, value: int = 0):
        v = int(value) & 0xFFFFFFFF
        if v >= 0x80000000:
            v -= 0x100000000
        return int.__new__(cls, v)


class Long(int):
    tag_id = TAG_LONG

    def __new__(cls, value: int = 0):
        v = int(value) & 0xFFFFFFFFFFFFFFFF
        if v >= 0x8000000000000000:
            v -= 0x10000000000000000
        return int.__new__(cls, v)


class Float(float):
    tag_id = TAG_FLOAT

    def __new__(cls, value: float = 0.0):
        # Round-trip through the 32-bit representation so a value written
        # and re-read compares equal, matching what Photon itself would see.
        packed = struct.pack(">f", float(value))
        return float.__new__(cls, struct.unpack(">f", packed)[0])


class Double(float):
    tag_id = TAG_DOUBLE

    def __new__(cls, value: float = 0.0):
        return float.__new__(cls, float(value))


class String(str):
    tag_id = TAG_STRING


class ByteArray(list):
    tag_id = TAG_BYTE_ARRAY

    def __init__(self, items: Optional[Iterable[int]] = None):
        super().__init__(items or [])


class IntArray(list):
    tag_id = TAG_INT_ARRAY

    def __init__(self, items: Optional[Iterable[int]] = None):
        super().__init__(items or [])


class LongArray(list):
    tag_id = TAG_LONG_ARRAY

    def __init__(self, items: Optional[Iterable[int]] = None):
        super().__init__(items or [])


class List(list):
    """TAG_List. `element_tag_id` must be set even when empty (spec section
    1.1 / 9.3): Photon's own files serialize empty lists with element type
    TAG_End, not with the "natural" type for that field. Use `List.empty()`
    for those, and always pass tagged values (Byte/Compound/... ) as items.
    """

    tag_id = TAG_LIST

    def __init__(self, element_tag_id: int, items: Optional[Iterable[Any]] = None):
        super().__init__(items or [])
        self.element_tag_id = element_tag_id

    @classmethod
    def empty(cls) -> "List":
        return cls(TAG_END, [])

    @classmethod
    def of(cls, items: PyList[Any]) -> "List":
        """Build a List from already-tagged items, inferring element_tag_id
        from the first item. Raises if the list is empty (ambiguous type) --
        use List.empty() explicitly for that case."""
        if not items:
            raise NBTError("List.of() needs at least one item; use List.empty() for a length-0 list")
        elem_id = _tag_id_of(items[0])
        return cls(elem_id, items)


class Compound(dict):
    """TAG_Compound. Plain dict subclass; insertion order is preserved
    (Python 3.7+ dict semantics) and used as the serialization order, purely
    for human-readable diffs -- NBT compounds are unordered maps, Photon does
    not care what order keys land in."""

    tag_id = TAG_COMPOUND


def _tag_id_of(value: Any) -> int:
    tag_id = getattr(value, "tag_id", None)
    if tag_id is None:
        raise TypeError(
            f"Value {value!r} of type {type(value).__name__} is not a tagged NBT value. "
            "Wrap it in nbt.Int/Float/String/Compound/List/... before writing."
        )
    return tag_id


# --- Reader ------------------------------------------------------------------


class _Reader:
    __slots__ = ("data", "pos")

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def _need(self, n: int) -> None:
        if self.pos + n > len(self.data):
            raise NBTError(f"Unexpected end of NBT data at offset {self.pos}, need {n} more bytes")

    def read_byte(self) -> int:
        self._need(1)
        v = self.data[self.pos]
        self.pos += 1
        if v >= 0x80:
            v -= 0x100
        return v

    def read_ubyte(self) -> int:
        self._need(1)
        v = self.data[self.pos]
        self.pos += 1
        return v

    def read_short(self) -> int:
        self._need(2)
        v = struct.unpack_from(">h", self.data, self.pos)[0]
        self.pos += 2
        return v

    def read_ushort(self) -> int:
        self._need(2)
        v = struct.unpack_from(">H", self.data, self.pos)[0]
        self.pos += 2
        return v

    def read_int(self) -> int:
        self._need(4)
        v = struct.unpack_from(">i", self.data, self.pos)[0]
        self.pos += 4
        return v

    def read_long(self) -> int:
        self._need(8)
        v = struct.unpack_from(">q", self.data, self.pos)[0]
        self.pos += 8
        return v

    def read_float(self) -> float:
        self._need(4)
        v = struct.unpack_from(">f", self.data, self.pos)[0]
        self.pos += 4
        return v

    def read_double(self) -> float:
        self._need(8)
        v = struct.unpack_from(">d", self.data, self.pos)[0]
        self.pos += 8
        return v

    def read_string(self) -> str:
        length = self.read_ushort()
        self._need(length)
        raw = self.data[self.pos:self.pos + length]
        self.pos += length
        return raw.decode("utf-8")

    def read_payload(self, tag_id: int) -> Any:
        if tag_id == TAG_BYTE:
            return Byte(self.read_byte())
        if tag_id == TAG_SHORT:
            return Short(self.read_short())
        if tag_id == TAG_INT:
            return Int(self.read_int())
        if tag_id == TAG_LONG:
            return Long(self.read_long())
        if tag_id == TAG_FLOAT:
            return Float(self.read_float())
        if tag_id == TAG_DOUBLE:
            return Double(self.read_double())
        if tag_id == TAG_BYTE_ARRAY:
            length = self.read_int()
            if length < 0:
                raise NBTError(f"Negative TAG_Byte_Array length {length}")
            self._need(length)
            raw = self.data[self.pos:self.pos + length]
            self.pos += length
            return ByteArray(b - 0x100 if b >= 0x80 else b for b in raw)
        if tag_id == TAG_STRING:
            return String(self.read_string())
        if tag_id == TAG_LIST:
            elem_id = self.read_ubyte()
            length = self.read_int()
            if length < 0:
                length = 0
            items = [self.read_payload(elem_id) for _ in range(length)]
            return List(elem_id, items)
        if tag_id == TAG_COMPOUND:
            comp = Compound()
            while True:
                child_id = self.read_ubyte()
                if child_id == TAG_END:
                    break
                name = self.read_string()
                comp[name] = self.read_payload(child_id)
            return comp
        if tag_id == TAG_INT_ARRAY:
            length = self.read_int()
            if length < 0:
                raise NBTError(f"Negative TAG_Int_Array length {length}")
            return IntArray(self.read_int() for _ in range(length))
        if tag_id == TAG_LONG_ARRAY:
            length = self.read_int()
            if length < 0:
                raise NBTError(f"Negative TAG_Long_Array length {length}")
            return LongArray(self.read_long() for _ in range(length))
        raise NBTError(f"Unknown tag id {tag_id} at offset {self.pos}")


def loads(data: bytes) -> Tuple[str, Compound]:
    """Parse a plain (non-gzipped) NBT byte string. Returns (root_name, root_compound).

    Photon's `.fxproj` files are exactly this: plain big-endian NBT starting
    with byte 0x0a (TAG_Compound) -- see docs/vfx-and-cinematics/PHOTON_FX_FORMAT.md section 1.2.
    """
    reader = _Reader(data)
    tag_id = reader.read_ubyte()
    if tag_id != TAG_COMPOUND:
        raise NBTError(f"Expected root TAG_Compound (10), got tag id {tag_id} ({_TAG_NAMES.get(tag_id, '?')})")
    name = reader.read_string()
    root = reader.read_payload(TAG_COMPOUND)
    if reader.pos != len(reader.data):
        raise NBTError(f"{len(reader.data) - reader.pos} trailing bytes after root compound")
    return name, root


def load_gzip(path: str) -> Tuple[str, Compound]:
    """Parse a gzipped NBT file. Photon's `.fx` files are gzip(NBT) -- see
    docs/vfx-and-cinematics/PHOTON_FX_FORMAT.md section 1.1."""
    with open(path, "rb") as f:
        raw = f.read()
    return loads(gzip.decompress(raw))


def load_plain(path: str) -> Tuple[str, Compound]:
    """Parse a plain (non-gzipped) NBT file, i.e. a `.fxproj`."""
    with open(path, "rb") as f:
        raw = f.read()
    return loads(raw)


# --- Writer ------------------------------------------------------------------


class _Writer:
    __slots__ = ("chunks",)

    def __init__(self):
        self.chunks: PyList[bytes] = []

    def w(self, b: bytes) -> None:
        self.chunks.append(b)

    def write_ubyte(self, v: int) -> None:
        self.w(struct.pack(">B", v & 0xFF))

    def write_short(self, v: int) -> None:
        self.w(struct.pack(">h", v))

    def write_ushort(self, v: int) -> None:
        self.w(struct.pack(">H", v))

    def write_int(self, v: int) -> None:
        self.w(struct.pack(">i", v))

    def write_long(self, v: int) -> None:
        self.w(struct.pack(">q", v))

    def write_float(self, v: float) -> None:
        self.w(struct.pack(">f", v))

    def write_double(self, v: float) -> None:
        self.w(struct.pack(">d", v))

    def write_string(self, s: str) -> None:
        raw = s.encode("utf-8")
        if len(raw) > 0xFFFF:
            raise NBTError(f"String too long for NBT (>{0xFFFF} bytes): {s[:50]!r}...")
        self.write_ushort(len(raw))
        self.w(raw)

    def write_payload(self, tag_id: int, value: Any) -> None:
        if tag_id == TAG_BYTE:
            self.write_ubyte(int(value) & 0xFF)
        elif tag_id == TAG_SHORT:
            self.write_short(int(value))
        elif tag_id == TAG_INT:
            self.write_int(int(value))
        elif tag_id == TAG_LONG:
            self.write_long(int(value))
        elif tag_id == TAG_FLOAT:
            self.write_float(float(value))
        elif tag_id == TAG_DOUBLE:
            self.write_double(float(value))
        elif tag_id == TAG_BYTE_ARRAY:
            self.write_int(len(value))
            self.w(bytes((b & 0xFF) for b in value))
        elif tag_id == TAG_STRING:
            self.write_string(str(value))
        elif tag_id == TAG_LIST:
            if not isinstance(value, List):
                raise NBTError(f"TAG_List payload must be an nbt.List, got {type(value).__name__}")
            self.write_ubyte(value.element_tag_id)
            self.write_int(len(value))
            for item in value:
                if value.element_tag_id != TAG_END:
                    got = _tag_id_of(item)
                    if got != value.element_tag_id:
                        raise NBTError(
                            f"List element tag mismatch: list declares element_tag_id="
                            f"{value.element_tag_id} ({_TAG_NAMES.get(value.element_tag_id)}) "
                            f"but item is {_TAG_NAMES.get(got, got)}"
                        )
                self.write_payload(value.element_tag_id, item)
        elif tag_id == TAG_COMPOUND:
            if not isinstance(value, dict):
                raise NBTError(f"TAG_Compound payload must be an nbt.Compound, got {type(value).__name__}")
            for key, child in value.items():
                child_tag_id = _tag_id_of(child)
                self.write_ubyte(child_tag_id)
                self.write_string(key)
                self.write_payload(child_tag_id, child)
            self.write_ubyte(TAG_END)
        elif tag_id == TAG_INT_ARRAY:
            self.write_int(len(value))
            for v in value:
                self.write_int(v)
        elif tag_id == TAG_LONG_ARRAY:
            self.write_int(len(value))
            for v in value:
                self.write_long(v)
        else:
            raise NBTError(f"Unknown tag id {tag_id}")

    def getvalue(self) -> bytes:
        return b"".join(self.chunks)


def dumps(root: Compound, root_name: str = "") -> bytes:
    """Serialize a root Compound to plain (non-gzipped) NBT bytes.

    `root_name` defaults to "" -- every observed Photon file (both `.fx` and
    `.fxproj`) uses an empty root name; see docs/vfx-and-cinematics/PHOTON_FX_FORMAT.md section 1.
    """
    if not isinstance(root, dict):
        raise NBTError(f"Root must be an nbt.Compound, got {type(root).__name__}")
    w = _Writer()
    w.write_ubyte(TAG_COMPOUND)
    w.write_string(root_name)
    w.write_payload(TAG_COMPOUND, root)
    return w.getvalue()


def dump_gzip(root: Compound, path: str, root_name: str = "") -> None:
    """Serialize and gzip-write a root Compound -- use for `.fx` files."""
    data = dumps(root, root_name)
    # mtime=0 keeps output byte-for-byte reproducible across runs.
    with open(path, "wb") as f:
        f.write(gzip.compress(data, compresslevel=9, mtime=0))


def dump_plain(root: Compound, path: str, root_name: str = "") -> None:
    """Serialize and write a root Compound with no compression -- use for
    `.fxproj` files."""
    data = dumps(root, root_name)
    with open(path, "wb") as f:
        f.write(data)


def _self_test() -> None:
    """Round-trips every NBT tag type through dumps()/loads(), including
    ones never observed in a real Photon file (Short, Double, the three
    array types) -- this module is a general NBT codec, not Photon-specific,
    so it must handle the full tag set correctly even though fx.py only
    emits a subset of it."""
    root = Compound({
        "a_byte": Byte(-5),
        "a_short": Short(-12345),
        "an_int": Int(-123456789),
        "a_long": Long(-1234567890123),
        "a_float": Float(3.5),
        "a_double": Double(2.718281828),
        "a_string": String("hello éè world"),
        "a_byte_array": ByteArray([1, -2, 3, -128, 127]),
        "an_int_array": IntArray([1, -2, 2147483647, -2147483648]),
        "a_long_array": LongArray([1, -2, 9223372036854775807, -9223372036854775808]),
        "empty_compound": Compound(),
        "empty_list": List.empty(),
        "list_of_int": List(TAG_INT, [Int(1), Int(2), Int(3)]),
        "list_of_compound": List(TAG_COMPOUND, [
            Compound({"x": Float(1.0)}),
            Compound({"x": Float(2.0), "nested": Compound({"y": String("z")})}),
        ]),
        "nested_list_of_list": List(TAG_LIST, [
            List(TAG_FLOAT, [Float(0.0), Float(1.0)]),
            List(TAG_FLOAT, [Float(2.0), Float(3.0), Float(4.0)]),
        ]),
    })

    data = dumps(root, root_name="")
    name, parsed = loads(data)
    assert name == "", f"root name round-trip failed: {name!r}"

    assert int(parsed["a_byte"]) == -5
    assert int(parsed["a_short"]) == -12345
    assert int(parsed["an_int"]) == -123456789
    assert int(parsed["a_long"]) == -1234567890123
    assert abs(float(parsed["a_float"]) - 3.5) < 1e-6
    assert abs(float(parsed["a_double"]) - 2.718281828) < 1e-9
    assert str(parsed["a_string"]) == "hello éè world"
    assert list(parsed["a_byte_array"]) == [1, -2, 3, -128, 127]
    assert list(parsed["an_int_array"]) == [1, -2, 2147483647, -2147483648]
    assert list(parsed["a_long_array"]) == [1, -2, 9223372036854775807, -9223372036854775808]
    assert isinstance(parsed["empty_compound"], Compound) and len(parsed["empty_compound"]) == 0
    assert isinstance(parsed["empty_list"], List) and len(parsed["empty_list"]) == 0
    assert parsed["empty_list"].element_tag_id == TAG_END
    assert [int(v) for v in parsed["list_of_int"]] == [1, 2, 3]
    assert len(parsed["list_of_compound"]) == 2
    assert str(parsed["list_of_compound"][1]["nested"]["y"]) == "z"
    assert len(parsed["nested_list_of_list"]) == 2
    assert len(parsed["nested_list_of_list"][1]) == 3

    # Byte-identical re-serialization (idempotency).
    data2 = dumps(parsed, root_name=name)
    assert data2 == data, "re-serialization was not byte-identical"

    # gzip round trip (the `.fx` path).
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        gz_path = os.path.join(tmp, "test.fx")
        dump_gzip(root, gz_path)
        gname, groot = load_gzip(gz_path)
        assert gname == ""
        assert int(groot["an_int"]) == -123456789

        plain_path = os.path.join(tmp, "test.fxproj")
        dump_plain(root, plain_path)
        pname, proot = load_plain(plain_path)
        assert pname == ""
        assert int(proot["a_long"]) == -1234567890123

    print("nbt.py self-test: all tag types round-trip correctly.")


if __name__ == "__main__":
    _self_test()
