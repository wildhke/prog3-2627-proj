"""Short demo script to show how a measurement file is loaded."""

from itertools import islice

from src.vehicle import Vehicle

file = "data/002.csv"

# No if/elif per file format: the vehicle chooses the matching reader by the file suffix (polymorphism)
vehicle = Vehicle.from_file(file)

print(vehicle.status)
print(vehicle.summary)
print(vehicle.data.to_dataframe().head())


def print_sample(sample):
    """Prints a data snipped in a defined manner."""
    print(f"t = {sample.time:6.2f} s | v = {sample.speed:6.1f} km/h | "
          f"a_x = {sample.accel_x:+.3f} g | a_y = {sample.accel_y:+.3f} g | "
          f"swa = {sample.steering_wheel_angle:+6.1f} deg")


samples = vehicle.samples(start=4000)  # Defines the start
print(type(samples))

print("\n")
print("One sample with next():")
print_sample(next(samples))  # with next, we can walk over an iterator -> next() returns the next value.


print("\n")
print("Chunk of 10 samples with islice():")
for sample in islice(samples, 10):  # islice takes a small chunk of 10 samples, only these 10 are computed
    print_sample(sample)


print("\n")
print("The next 3 samples continue:")
for sample in islice(samples, 3):  # generators remember its positions: the next chunk continues where the last one stopped
    print_sample(sample)


# Own generator function: splits any iterable into chunks of a given size and provide those batches.
def chunks(iterable, size):
    """Yields lists of size elements until the iterable is exhausted."""
    iterator = iter(iterable)
    while chunk := list(islice(iterator, size)):
        yield chunk


print("\n")
print("Chunks of 10 samples (every 100th sample = 1 s), mean velocity per chunk:")
for number, chunk in enumerate(chunks(vehicle.samples(step=100), 10)):
    mean_speed = sum(sample.speed for sample in chunk) / len(chunk)
    print(f"chunk {number}: {chunk[0].time:5.1f} s - {chunk[-1].time:5.1f} s | mean v = {mean_speed:5.1f} km/h")
