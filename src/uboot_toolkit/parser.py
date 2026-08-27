"""Parsers for detected binary structures"""
from dataclasses import dataclass

from uboot_toolkit.structure import FDT_PROP, StructureToken


DTB_HEADER_SIZE = 40
DTB_MAGIC = 0xD00DFEED


@dataclass(frozen=True)
class DtbHeader:
    """Represent the header of a Device Tree Blob."""
    magic: int
    total_size: int
    structure_offset: int
    strings_offset: int
    memory_reservation_offset: int
    version: int
    last_compatible_version: int
    boot_cpu_id: int
    structure_size: int
    strings_size: int

def parse_dtb_header(data: bytes, offset: int = 0) -> DtbHeader:
    """Parse a DTB header at the given offset."""
    if offset < 0:
        raise ValueError("Offset must not be negative.")

    if len(data) < offset + DTB_HEADER_SIZE:
        raise ValueError("Not enough data for a DTB header.")

    magic = int.from_bytes(data[offset:offset + 4], "big")

    if magic != DTB_MAGIC:
        raise ValueError(
            f"Invalid DTB magic: 0x{magic:08X}"
        )

    values = [
        int.from_bytes(
            data[offset + start:offset + start + 4],
            "big",
        )
        for start in range(4, DTB_HEADER_SIZE, 4)
    ]

    return DtbHeader(
        magic=magic,
        total_size=values[0],
        structure_offset=values[1],
        strings_offset=values[2],
        memory_reservation_offset=values[3],
        version=values[4],
        last_compatible_version=values[5],
        boot_cpu_id=values[6],
        structure_size=values[8],
        strings_size=values[7],
    )

def get_dtb_structure_bounds(
    header: DtbHeader,
    offset: int = 0,
) -> tuple[int, int]:
    """Return absolute start and end offsets of the DTB structure block."""
    if offset < 0:
        raise ValueError("Offset must not be negative.")

    structure_start = offset + header.structure_offset
    structure_end = structure_start + header.structure_size

    if structure_end > offset + header.total_size:
        raise ValueError("DTB structure extends beyond the DTB.")

    return structure_start, structure_end


def resolve_dtb_string(
    data: bytes,
    strings_offset: int,
    strings_size: int,
    name_offset: int,
) -> str:
    """Resolve a null-terminated string from the DTB strings block."""
    if strings_offset < 0:
        raise ValueError("Strings offset must not be negative.")

    if strings_size < 0:
        raise ValueError("Strings size must not be negative.")

    if name_offset < 0:
        raise ValueError("Name offset must not be negative.")

    strings_end = strings_offset + strings_size

    if strings_end > len(data):
        raise ValueError("DTB strings block extends beyond the data.")

    if name_offset >= strings_size:
        raise ValueError("Property name offset is outside the strings block.")

    string_start = strings_offset + name_offset
    string_end = string_start

    while string_end < strings_end and data[string_end] != 0:
        string_end += 1

    if string_end >= strings_end:
        raise ValueError("DTB string is not null-terminated.")

    return data[string_start:string_end].decode(
        "ascii",
        errors="replace",
    )


def resolve_property_name(
    token: StructureToken,
    data: bytes,
    strings_offset: int,
    strings_size: int,
) -> str:
    """Resolve the name of a DTB property token."""

    if token.property_name_offset is None:
        raise ValueError("Token does not contain a property name offset.")

    if token.token != FDT_PROP:
        raise ValueError("Token is not a property token.")

    return resolve_dtb_string(
        data=data,
        strings_offset=strings_offset,
        strings_size=strings_size,
        name_offset=token.property_name_offset,
    )


def build_dtb_property(
    token: StructureToken,
    data: bytes,
    strings_offset: int,
    strings_size: int,
):
    """Convert a property token into a DtbProperty."""

    if token.token != FDT_PROP:
        raise ValueError("Token is not a property token.")

    if token.property_name_offset is None:
        raise ValueError("Property token has no name offset.")

    if token.property_value is None:
        raise ValueError("Property token has no value.")

    name = resolve_dtb_string(
        data=data,
        strings_offset=strings_offset,
        strings_size=strings_size,
        name_offset=token.property_name_offset,
    )

    from uboot_toolkit.structure import DtbProperty

    return DtbProperty(
        name=name,
        value=token.property_value,
    )


def convert_dtb_properties(
    node,
    data: bytes,
    strings_offset: int,
    strings_size: int,
):
    """Convert property tokens in a DTB tree into DtbProperty objects."""

    converted_properties = []

    for property_item in node.properties:
        converted_properties.append(
            build_dtb_property(
                token=property_item,
                data=data,
                strings_offset=strings_offset,
                strings_size=strings_size,
            )
        )

    node.properties = converted_properties

    for child in node.children:
        convert_dtb_properties(
            node=child,
            data=data,
            strings_offset=strings_offset,
            strings_size=strings_size,
        )

    return node