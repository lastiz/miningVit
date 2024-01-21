import random
from string import ascii_uppercase, digits


_CODE_SYMBOLS: str = ascii_uppercase + digits


def gen_rand_alphanum_str(length: int) -> str:
    """Create random alpha-numeric uppercase string with length == :length

    Args:
        length (int): String length

    Raises:
        ValueError: Raises if :length > 36

    Returns:
        str: Random uppercase alpha-numeric string with length == :length
    """
    if length > len(_CODE_SYMBOLS):
        raise ValueError(f"Length must be lower or equal 36")
    return "".join(random.choices(_CODE_SYMBOLS, k=length))
