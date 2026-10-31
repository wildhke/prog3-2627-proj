"""Short demo script to show how a reader can be implemented."""

from src.vehicle import Vehicle

file = ""

class MatlabReaderNotImplementedError(BaseException):
    pass


if file.endswith("csv"):
    print("We need to load a csv-file")
    print("\n"*3)
    try:
        measurement_vehicle = Vehicle.from_csv(file)

    except Exception as e:
        print(f"Error occurred while loading CSV file: {e}")

elif file.endswith("mat"):
    try:
        print("We need to load a mat-file")
        print("\n"*3)
        measurement_vehicle = Vehicle.from_mat(file)

    except Exception as e:
        raise MatlabReaderNotImplementedError(f"Missing function to read MAT-files") from e

else:
    print(f"We need to load a {file.split(".")[-1]} file")
    raise NotImplementedError(f"Missing function to read {file.split(".")[-1]}-files")


print(measurement_vehicle.data.head())