class EntitySummary:
    def __init__(self):
        self.count = 0
        self.breakdown = dict()

    def __add__(self, other: 'EntitySummary') -> 'EntitySummary':
        """
        adds two EntitySummary together
        :param other:
        :return: self
        """
        self.count += other.count
        for (key, val) in other.breakdown.items():
            if key in self.breakdown:  # ..do an add
                self.breakdown[key]['count'] += val['count']
            else:
                self.breakdown[key] = val

        return self
