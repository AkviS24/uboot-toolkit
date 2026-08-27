from dataclasses import dataclass


FDT_BEGIN_NODE = 0x00000001
FDT_END_NODE = 0x00000002
FDT_PROP = 0x00000003
FDT_NOP = 0x00000004
FDT_END = 0x00000009


@dataclass
class StructureToken:
    offset: int
    token: int
    name: str


TOKEN_NAMES = {
    FDT_BEGIN_NODE: "BEGIN_NODE",
    FDT_END_NODE: "END_NODE",
    FDT_PROP: "PROP",
    FDT_NOP: "NOP",
    FDT_END: "END",
}


def parse_structure(data: bytes, offset: int, size: int) -> list[StructureToken]:
    """Parse the DTB structure block and return its tokens."""

    end = offset + size
    position = offset
    tokens = []

    while position < end:
        token = int.from_bytes(data[position:position + 4], "big")

        if token not in TOKEN_NAMES:
            break

        tokens.append(
            StructureToken(
                offset=position,
                token=token,
                name=TOKEN_NAMES[token],
            )
        )

        position += 4

        if token == FDT_END:
            break

        if token == FDT_BEGIN_NODE:
            while position < end and data[position] != 0:
                position += 1

            position += 1

            while position % 4 != 0:
                position += 1

        elif token == FDT_PROP:
            if position + 8 > end:
                break

            property_length = int.from_bytes(
                data[position:position + 4],
                "big",
            )

            property_end = position + 8 + property_length

            if property_end > end:
                break

            position = property_end

            while position % 4 != 0:
                position += 1

            if position > end:
                break

    return tokens