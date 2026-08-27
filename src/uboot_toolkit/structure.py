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
    node_name: str | None = None
    property_length: int | None = None
    property_name_offset: int | None = None
    property_value: bytes | None = None


@dataclass
class DtbNode:
    name: str
    children: list["DtbNode"]
    properties: list[StructureToken]


@dataclass
class DtbProperty:
    name: str
    value: bytes


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
            node_name_start = position

            while position < end and data[position] != 0:
                position += 1

            if position >= end:
                break

            node_name = data[node_name_start:position].decode(
                "ascii",
                errors="replace",
            )

            tokens[-1].node_name = node_name

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

            property_name_offset = int.from_bytes(
                data[position + 4:position + 8],
                "big",
            )

            property_value_start = position + 8
            property_end = property_value_start + property_length

            if property_end > end:
                break

            property_value = data[property_value_start:property_end]

            tokens[-1].property_length = property_length
            tokens[-1].property_name_offset = property_name_offset
            tokens[-1].property_value = property_value

            position = property_end

            while position % 4 != 0:
                position += 1

            if position > end:
                break

    return tokens


def build_dtb_tree(tokens: list[StructureToken]) -> DtbNode:
    """Build a DTB node tree from structure tokens."""
    root: DtbNode | None = None
    stack: list[DtbNode] = []

    for token in tokens:
        if token.token == FDT_BEGIN_NODE:
            if token.node_name is None:
                raise ValueError("BEGIN_NODE token has no node name.")

            node = DtbNode(
                name=token.node_name,
                children=[],
                properties=[],
            )

            if stack:
                stack[-1].children.append(node)
            else:
                if root is not None:
                    raise ValueError("Multiple root nodes found.")

                root = node

            stack.append(node)

        elif token.token == FDT_END_NODE:
            if not stack:
                raise ValueError("END_NODE without matching BEGIN_NODE.")

            stack.pop()

        elif token.token == FDT_PROP:
            if not stack:
                raise ValueError("PROP outside of a DTB node.")

            stack[-1].properties.append(token)

        elif token.token == FDT_END:
            break

    if root is None:
        raise ValueError("No root node found.")

    if stack:
        raise ValueError("Unclosed DTB node.")

    return root
