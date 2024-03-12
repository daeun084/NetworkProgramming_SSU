if __name__ == '__main__':
    #Decode
    input_byte = b'\xff\xfe4\x001\x003\x00 \x00i\x00s\x00 \x00i\x00n\x00n\x00. \x00'
    input_characters = input_byte.decode('utf-16')
    print(repr(input_characters))

    #Encode
    output_characters = 'We copy you down, Eagle.\n'
    output_byte = output_characters.encode('utf-8')
    with open('eagle.txt', 'wb') as f:
        f.write(output_byte)