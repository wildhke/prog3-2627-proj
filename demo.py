"""Short demo script to show how a reader can be implemented."""

from src.vehicle import Vehicle

file = "data/002.mat"

# File-specific decision:
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
    except:
        print("Failed.")


else:
    print(f"We need to load a {file.split(".")[-1]} file")
    raise NotImplementedError(f"Missing function to read {file.split(".")[-1]}-files")
print(measurement_vehicle.data.head())


# Do it with for all file types without the need of checking its type, adding new checks for new file formats etc.
vec = Vehicle.from_file(file)
print(vec.data.head())
