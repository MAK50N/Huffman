import bisect
import math
import time


def str_freq(file_path):
    freqs = dict()
    s = b""
    with open(file_path, "rb") as f:
        byte = f.read(1)
        s += byte
        while byte:
            if byte in freqs:
                freqs[byte] += 1
            else:
                freqs[byte] = 1
            byte = f.read(1)
            s += byte
        f.close()


    return freqs


def file_freq(name):
    with open(name) as f:
        return str_freq(f.read())


class TreeNode(object):

    def __init__(self, key, data, children=[]):
        self.key = key
        self.data = data
        self.children = children

    def print(self):
        def _print(node, level):
            print("\t" * level + str((node.key, node.data)))
            for child in node.children:
                _print(child, level + 1)

        _print(self, 0)

    def __eq__(self, other):
        return self.key == other.key

    def __ne__(self, other):
        return self.key != other.key

    def __lt__(self, other):
        return self.key < other.key

    def __le__(self, other):
        return self.key <= other.key

    def __gt__(self, other):
        return self.key > other.key

    def __ge__(self, other):
        return self.key >= other.key


def huffman_initial_count(message_count, digits):
    if message_count <= 0:
        raise ValueError("cannot create Huffman tree with <= 0 messages!")
    if digits <= 1:
        raise ValueError("must have at least two digits for Huffman tree!")

    if message_count == 1:
        return 1

    return 2 + (message_count - 2) % (digits - 1)


def combine_and_replace(nodes, n):
    group = nodes[:n]
    combined = TreeNode(sum(node.key for node in group), None, group)
    nodes = nodes[n:]
    bisect.insort(nodes, combined)

    return nodes


def huffman_nary_tree(probabilities, digits):
    if digits <= 1:
        raise ValueError("must have at least 2 digits!")

    if len(probabilities) == 0:
        raise ValueError("cannot create a tree with no messages!")

    if len(probabilities) == 1:
        symbol, freq = probabilities[0]
        if freq != 1:
            print("The probabilities sum to {} (!= 1)...".format(freq))
        if math.isclose(probabilities[0].key, 1.0):
            print("(but they are close)")

        return TreeNode(freq, symbol)

    probabilities = [TreeNode(freq, symbol) for (symbol, freq) in probabilities]
    probabilities = sorted(probabilities)

    initial_count = huffman_initial_count(len(probabilities), digits)
    probabilities = combine_and_replace(probabilities, initial_count)

    while len(probabilities) != 1:
        probabilities = combine_and_replace(probabilities, digits)

    return probabilities.pop()


def indicies_to_code(path, digits):
    combination = ""
    for index in path:
        if index < 0:
            raise ValueError("cannot accept negative path indices (what went wrong?)")
        if index >= digits:
            raise ValueError("cannot have an index greater than the number of digits!")

        combination += baseN(index, digits)

    return combination


def huffman_nary_dict(root, digits):
    def visit(node, path, decoding_dict):
        if len(node.children) == 0:
            code = indicies_to_code(path, digits)
            decoding_dict[code] = node.data
        else:
            for k, child in enumerate(node.children):
                path.append(k)
                visit(child, path, decoding_dict)
                path.pop()

    decoding_dict = dict()
    visit(root, [], decoding_dict)

    return decoding_dict


def inverse_dict(original):
    ret = dict()

    for key, value in original.items():
        ret[value] = key

    return ret


def baseN(num, b, numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
    return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])



class Encoder:
    def __init__(self, file_input, file_output, digits):
        self.freqs = str_freq(file_input)
        self.probabilities = list(self.freqs.items())
        self.huff = huffman_nary_tree(self.probabilities, digits)
        self.huffman_table = huffman_nary_dict(self.huff, digits)
        self.inv_huffman_table = inverse_dict(self.huffman_table)

        self.__write__(file_output, file_input)

    def __write__(self, file_output, file_input):
        encode = b""
        with open(file_input, "rb") as file:
            byte = file.read(1)
            while byte:
                en = self.inv_huffman_table[byte].encode()
                encode += en
                byte = file.read(1)
            file.close()
        out = open(file_output, mode="wb")
        out.write(encode)
        out.close()

class Decoder:
    def __init__(self, file_input, file_output, huffman_table):
        with open(file_input, "rb") as f:
            self.input_data = f.read()
            f.close()

        decode = b""
        string = self.input_data
        while string:
            # Huffman codes are prefix free, so read until we find a code.
            for index in range(len(string) + 1):
                if string[:index].decode() in huffman_table:
                    break
            code = string[:index].decode()
            decode += huffman_table[code]
            string = string[index:]

        out = open(file_output, "wb")
        out.write(decode)
        out.close()


if __name__ == '__main__':
    file = "test.txt"
    start = time.time()
    enc16 = Encoder(file, "compressed3.huf", 3)
    end = time.time()
    print("Encoding 16 time: ", end - start, "seconds")
    start = time.time()
    dec16 = Decoder("compressed3.huf", "decompressed3.txt", enc16.huffman_table)
    end = time.time()
    print("Decoding 16 time: ", end - start, "seconds")
    print(enc16.huffman_table)

    print()

    start = time.time()
    enc2 = Encoder(file, "compressed2.huf", 2)
    end = time.time()
    print("Encoding 2 time: ", end - start, "seconds")
    start = time.time()
    dec2 = Decoder("compressed2.huf", "decompressed2.txt", enc2.huffman_table)
    end = time.time()
    print("Decoding 2 time: ", end - start, "seconds")
    print(enc2.huffman_table)



