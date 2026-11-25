"""
O: Open/Closed

Open for extension but closed for modification.
"""


# Every new file format changes this function
def load_with_if(file):
    if file.endswith(".csv"):
        return "csv data"
    elif file.endswith(".json"):
        return "json data"
    raise ValueError(f"unknown format: {file}")


try:
    load_with_if("drive.mat")  # new format -> edit the function
except ValueError as error:
    print("BEFORE:", error)


# -----------------------------------------
# O-conform: Ine class per format. load() never changes
# -----------------------------------------
class CsvReader:
    def read(self, file):
        return "csv data"


class JsonReader:
    def read(self, file):
        return "json data"


READERS = {".csv": CsvReader(), ".json": JsonReader()}


def load(file):
    suffix = file[file.rfind("."):]
    return READERS[suffix].read(file)


print(load("drive.csv"))


# Extension: a new class plus one entry - load() stays untouched
class MatReader:
    def read(self, file):
        return "mat data"


READERS[".mat"] = MatReader()
print(load("drive.mat"))
