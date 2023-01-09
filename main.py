import concurrent.futures
import logging
import multiprocessing
import pathlib
import string
from typing import NamedTuple, Final, Iterator
from custom_logger import CustomFormatter
from math import ceil
import time


# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

# Create paths for writing into a file
here = pathlib.Path(__file__).parent  # get current directory
outpath = here.joinpath("output")  # create "output" subdirectory


# Quantity of logical cores on machine
CPUs = multiprocessing.cpu_count()


class ActionArgs(NamedTuple):
    alphabet: str
    number_of_start_word: int
    word_length: int
    start_word_as_digits: list[int]
    word: str
    package_number: int


def generate_words_for_current_package(
    alphabet: str,
    number_of_start_word: int,
    word_length: int,
    start_word_as_digits: list[int],
    word: str,
    package_number: int,
) -> list[str]:
    list_of_package_words = []
    for _ in range(qtty_of_items_in_package):
        word_as_digits = list(
            convert_decimal_number_to_custom_base(
                number=number_of_start_word, base=alphabet_length, word_length=word_length
            )
        )
        word = "".join([alphabet[character_index] for character_index in word_as_digits])
        # logger.info(f'{word}')
        number_of_start_word += 1
        list_of_package_words.append(word)
        if word == alphabet[-1] * word_length:
            break
    write_to_file(list_of_package_words=list_of_package_words, file=package_number)
    return list_of_package_words


def __wrapper(args: ActionArgs) -> list[str]:
    logger.debug(f"{args=}")
    return generate_words_for_current_package(**args._asdict())


def convert_decimal_number_to_custom_base(number: int, base: int, word_length: int) -> Iterator[int]:
    """Convert decimal integer to list of numbers for custom base by iteration. From lowest to bigger."""

    list_of_numbers_to_convert = [0 for _ in range(word_length)]
    counter = word_length - 1
    number_to_convert = number

    while number_to_convert:
        floor_division, remainder = divmod(number_to_convert, base)
        list_of_numbers_to_convert[counter] = remainder
        number_to_convert = floor_division
        counter -= 1

    return list_of_numbers_to_convert


def write_to_file(list_of_package_words: list, file):
    with open(f"{outpath}/package {file}.txt", "w") as f:
        for word in list_of_package_words:
            f.write(f"{word}\n")


def main():
    packages = [
        ActionArgs(
            alphabet=alphabet,
            number_of_start_word=qtty_of_items_in_package * package_number,
            word_length=word_length,
            start_word_as_digits=list(
                convert_decimal_number_to_custom_base(
                    number=qtty_of_items_in_package * package_number, base=alphabet_length, word_length=word_length
                )
            ),
            word="".join(
                [
                    alphabet[character_index]
                    for character_index in list(
                        convert_decimal_number_to_custom_base(
                            number=qtty_of_items_in_package * package_number,
                            base=alphabet_length,
                            word_length=word_length,
                        )
                    )
                ]
            ),
            package_number=package_number,
        )
        for package_number in range(qtty_of_packages)
    ]
    with concurrent.futures.ProcessPoolExecutor(CPUs) as executor:
        executor.map(
            __wrapper,
            packages,
        )


if __name__ == "__main__":
    alphabet = string.ascii_lowercase + string.digits
    alphabet_length = len(alphabet)
    word_length = 5
    total_number_of_words: Final[int] = len(alphabet) ** word_length
    logger.warning(f"{alphabet=}, {word_length=}, {total_number_of_words=}")
    qtty_of_items_in_package = 1000000
    qtty_of_packages = ceil(total_number_of_words / qtty_of_items_in_package)
    CustomFormatter()
    start = time.perf_counter()
    main()
    elapsed = time.perf_counter() - start
    logger.warning(f"Program completed in {elapsed:0.5f} seconds.")
    logger.warning(f"Total generated packages: {qtty_of_packages}")
    logger.info(f"All data written to files in f'{outpath}")
