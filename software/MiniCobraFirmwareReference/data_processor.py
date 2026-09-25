def twos_comp_filter(data, bytes):
    """
    Convert the data into correct integer value according to 
    two's complement.

    Args:
        data (int) : integer data representation in two's complement
        bytes (int) : number of bytes 2 or 4

    Returns:
        int: value of data in integer form, converted from twos complement
    """
    # lead_bitmask should mask off the first bit to check for the negative bit
    if bytes == 2 or bytes == 1 or bytes == 4:
        lead_bitmask = 2**((bytes * 8) - 1)
    else:
        raise ValueError("invalid bytes size")
    data = int(data)
    if data & lead_bitmask == lead_bitmask:
        # flip all bit in mask and return data masked
        return (data & (~(lead_bitmask))) - lead_bitmask
    else:
        return data