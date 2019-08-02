import bitstring

def convert_8_to_10_bit_words(bitarray):
    raw_binary_str = bitarray.bin

    converted = ""

    word = ""
    num_odd = 0
    for i in raw_binary_str:
        if i == '1':
            num_odd = (num_odd + 1) % 2

        word = word + i

        if len(word) == 8:
            num_even = 0

            if num_odd == 0:
                num_even = 1

            converted = converted + str(num_even) + str(num_odd) + word
            word = ""
            num_odd = 0

    return converted

def int_to_bin(value, num_bits=1):
    raw = bin(value).lstrip("0b")

    num_missing_bits = num_bits - len(raw)

    raw = "0" * num_missing_bits + raw

    return raw

def bool_to_bin(bool_val):
    return int_to_bin(int(bool_val))

def offset_reader(bitarray_data, bit_offset):
    bitarray_data.pos += bit_offset
