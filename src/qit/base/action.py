class Action(object):
    def __init__(self, iterator_factory):
        self.iterator_factory = iterator_factory

    def run(self, parallel=False):
        from session import session

        with session.create_context(parallel) as ctx:
            try:
                ctx.run(self.iterator_factory.copy(), self)
            finally:
                session.destroy_context(ctx)

        return self.get_result()

    def get_result(self):
        raise NotImplementedError()

    def handle_item(self, item):
        raise NotImplementedError()


class Collect(Action):
    def __init__(self, iterator_factory):
        super(Collect, self).__init__(iterator_factory)
        self.items = []

    def handle_item(self, item):
        self.items.append(item)
        return True

    def get_result(self):
        return self.items


class First(Action):
    def __init__(self, iterator_factory, fn=None, default=None):
        super(First, self).__init__(iterator_factory)
        self.fn = fn
        self.default = default
        self.result = None

    def handle_item(self, item):
        assert self.result is None

        if self.fn is None or self.fn(item):
            self.result = item
            return False
        else:
            return True

    def get_result(self):
        if self.result is not None:
            return self.result
        else:
            return self.default


class Reduce(Action):
    def __init__(self, iterator_factory, fn, init=0):
        super(Reduce, self).__init__(iterator_factory)
        self.fn = fn
        self.value = init

    def handle_item(self, item):
        self.value = self.fn(item, self.value)
        return True

    def get_result(self):
        return self.value


class MaxAll(Action):
    def __init__(self, iterator_factory, key_fn):
        super(MaxAll, self).__init__(iterator_factory)
        self.best_results = None
        self.best_value = None
        self.key_fn = key_fn

    def handle_item(self, item):
        value = self.key_fn(item)
        if self.best_value is None or value > self.best_value:
            self.best_value = value
            self.best_results = [item]
        elif value == self.best_value:
            self.best_results.append(item)
        return True

    def get_result(self):
        return self.best_results