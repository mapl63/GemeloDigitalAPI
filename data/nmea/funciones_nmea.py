def calculate_nmea_checksum(sentence):

    data = sentence.split('*')[0][1:]

    checksum = 0

    for char in data:
        checksum ^= ord(char)

    return '{:02X}'.format(checksum)


def decimal_to_nmea(coord, is_lat):

    c = abs(coord)
    grados = int(c)
    minutos = (c - grados) * 60

    if is_lat:
        hemi = 'N' if coord >= 0 else 'S'
        return f"{grados:02d}{minutos:07.4f}", hemi
    else:
        hemi = 'E' if coord >= 0 else 'W'
        return f"{grados:03d}{minutos:07.4f}", hemi
