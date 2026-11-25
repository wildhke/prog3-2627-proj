"""
D: Dependency Inversion

Depend on abstractions, not on details.
"""
from abc import ABC, abstractmethod


class Exporter(ABC):  # the abstraction
    @abstractmethod
    def export(self, values) -> str: ...


class CsvExporter(Exporter):  # a detail
    def export(self, values):
        return ";".join(map(str, values))


# The report creates detail by itself -> always CSV, hard to test
class ReportBefore:
    def __init__(self):
        self.exporter = CsvExporter()  # fixed dependency

# -----------------------------------------
# D-conform: The report receives the abstraction from outside
# -----------------------------------------
class Report:
    def __init__(self, exporter: Exporter):
        self.exporter = exporter  # injected

    def save(self, values):
        return self.exporter.export(values)


class FakeExporter(Exporter):  # e.g. for a test
    def export(self, values):
        return f"{len(values)} values exported"


print(Report(CsvExporter()).save([0, 30, 55]))
print(Report(FakeExporter()).save([0, 30, 55]))
