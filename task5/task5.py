import itertools


class CustomLinq:
    def __init__(self, sequence):
        self.sequence = sequence

    def select(self, operation):
        return CustomLinq(map(operation, self.sequence))

    def flatten(self):
        return CustomLinq([item for sublist in self.sequence for item in sublist])

    def where(self, predicate):
        return CustomLinq(filter(predicate, self.sequence))

    def take(self, k):
        return CustomLinq(itertools.islice(self.sequence, k))

    def group_by(self, operation):
        result = {}
        for key, group in itertools.groupby(self.sequence, operation):
            if key not in result:
                result[key] = []
            for value in group:
                result[key].append(value)
        return CustomLinq(list(result.items()))

    def order_by(self, operation):
        return CustomLinq(sorted(self.sequence, key=operation))

    def to_list(self):
        return list(self.sequence)


def fibonacci():
    item0 = 0
    item1 = 1
    while True:
        yield item0
        print("fibonacci function generated " + str(item0))
        temp = item0
        item0 = item1
        item1 += temp

# Поток чисел Фибоначчи
print(
    CustomLinq(
        fibonacci()).where(lambda x: x % 3 == 0).select(
        lambda x: x ** 2 if x % 2 == 0 else x).take(5).to_list()
)

with open('task5.txt', 'r') as f:
    tokenized_text = f.read().replace('\n', ' ').split()

# Word Count
print(
    CustomLinq(tokenized_text).group_by(lambda x: x).order_by(
        lambda x: -len(x[1])).select(lambda x: (x[0], len(x[1]))).to_list()
)
