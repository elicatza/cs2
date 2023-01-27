#!/usr/bin/env python3
import sys


def main():

    words: dict = {}
    word_buffer = ""

    while True:
        try:
            # Read one byte at a time
            char = sys.stdin.read(1)
        except KeyboardInterrupt:
            exit(0)

        # EOF == ""
        # Done reading from stdin
        if char == "":
            break

        match char:
            case '.' | '?' | '!' | ' ' | '\n':
                if word_buffer == "":
                    continue
                if word_buffer not in words:
                    words[word_buffer] = 1
                else:
                    words[word_buffer] += 1
                word_buffer = ""
            case _:
                word_buffer += char

    # Sort dictinary by value
    sorted_words = dict(sorted(words.items(), key=lambda x: x[1], reverse=True))

    for k, v in sorted_words.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
