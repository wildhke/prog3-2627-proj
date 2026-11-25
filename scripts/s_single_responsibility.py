"""
S: Single Responsibility

One class & only one reason to change

"""


# Three reasons to change in one class (default behavior)
class VehicleBefore:
    def __init__(self, speeds):
        self.speeds = speeds

    @property
    def max_speed(self):
        return max(self.speeds)

    def to_csv(self):
        return "speed\n" + "\n".join(map(str, self.speeds))

    def show(self):
        print(f"Max speed: {self.max_speed} km/h")

# -----------------------------------------
# S-conform: One class per reason to change
# -----------------------------------------

class Vehicle:       # changes with the vehicle logic
    def __init__(self, speeds):
        self.speeds = speeds

    @property
    def max_speed(self):
        return max(self.speeds)


class CsvExporter:
    def export(self, vehicle):
        return "speed\n" + "\n".join(map(str, vehicle.speeds))


class ConsoleView:
    def show(self, vehicle):
        print(f"Max speed: {vehicle.max_speed} km/h")


vehicle = Vehicle([0, 30, 55, 50])
ConsoleView().show(vehicle)
print(CsvExporter().export(vehicle))
