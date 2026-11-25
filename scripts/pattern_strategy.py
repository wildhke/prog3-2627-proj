"""Strategy: Exchangeable behavior as its own object.

When is it useful?
A project monitors a test drive and identifies the driving maneuver. Each
maneuver needs its own evaluation with different KPIs:
- curve:           max lateral acceleration, steering wheel angle
- lane change:     duration, lateral offset, steering rate
- emergency brake: deceleration, stopping distance, reaction time

Each evaluation is one strategy class with the same method, for instance 
evaluate(drive). The monitor only calls evaluate() on the strategy that fits
the detected maneuver. A new maneuver is a new class, the monitor itself
stays unchanged (Open/Closed).
"""


class MeanSpeed:
    def compute(self, speeds):
        return sum(speeds) / len(speeds)


class MaxSpeed:
    def compute(self, speeds):
        return max(speeds)


class SpeedReport:
    def __init__(self, strategy):
        self.strategy = strategy # the exchangeable part

    def show(self, speeds):
        print(type(self.strategy).__name__, self.strategy.compute(speeds))


speeds = [0, 30, 55, 50]
report = SpeedReport(MeanSpeed())
report.show(speeds)
report.strategy = MaxSpeed() # swap at runtime
report.show(speeds)

# In Python a strategy can also be a plain function, e.g. key= in sorted()
print(sorted(["drive.json", "a.csv", "trip.mat"], key=len))
