"""
L: Liskov Substitution

A subclass must work wherever its base works.
"""


class Reader:
    def read(self, file) -> list:
        return [0, 30, 55]


class CsvReader(Reader):
    def read(self, file) -> list:  # same parameters, same type
        return [0, 40, 80]


# The subclass changes the contract of read()
class SemicolonReader(Reader):
    def read(self, file, sep) -> dict:  # new parameter, other return type
        return {"speed": [0, 20]}


for reader in [Reader(), CsvReader(), SemicolonReader()]:
    try:
        print(type(reader).__name__, max(reader.read("drive.csv")))
    except TypeError as error:
        print(type(reader).__name__, "breaks the caller:", error)

# -----------------------------------------
# L-conform: Configure the subclass in the constructor, keep the contract/template
# -----------------------------------------
class SemicolonReader(Reader):
    def __init__(self, sep=";"):
        self.sep = sep

    def read(self, file) -> list:
        return [0, 20]


print("SemicolonReader", max(SemicolonReader().read("drive.csv")))
