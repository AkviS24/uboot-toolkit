"""Parsers for detected binary structures"""
from dataclasses import dataclass


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
        structure_size=values[7],
        strings_size=values[8],
    )