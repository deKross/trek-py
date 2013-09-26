class Query(object):
    def __init__(self, *args, **kwargs):
        self.queryset = None
        if args and isinstance(args[0], list):
            self.queryset = list(args[0])
            return
        self.queryset = self._filter(*args, **kwargs)

    def __iter__(self):
        return iter(self.queryset)

    def random(self, count=1):
        if count > 1:
            return random.sample(self.queryset, count)
        return random.choice(self.queryset)

    def _filter(self, *args, **kwargs):
        def quadsec():
            result = []
            for gal in Galaxy._instances:
                for quad in gal:
                    if quadrant_check is None or quadrant_check(quad):
                        for sec in quad:
                            if sec.obj is not None and (sector_check is None or sector_check(sec)):
                                if (type_check is None or type_check(sec.obj)) and \
                                   (object_check is None or object_check(sec.obj)):
                                    result.append(sec.obj)
            return result

        quadrant_check = sector_check = type_check = object_check = None

        types = set()
        for arg in args:
            types.update(arg.split())
        arg = kwargs.get('type')
        if arg is not None:
            types.update(arg.split())

        if types:
            type_check = lambda obj: obj.__class__.__name__ in types

        if self.queryset:
            queryset_set = set(self.queryset)
            object_check = lambda obj: obj in queryset_set

        sector = kwargs.get('sector')
        if sector is not None:
            if isinstance(sector, (tuple, list)):
                sector_check = lambda sec: sec in sector
            else:
                sector_check = lambda sec: sec is sector
        else:
            quadrant = kwargs.get('quadrant')
            if quadrant is not None:
                if isinstance(quadrant, (tuple, list)):
                    quadrant_check = lambda quad: quad in quadrant
                else:
                    quadrant_check = lambda quad: quad is quadrant

        return quadsec()

    def filter(self, *args, **kwargs):
        return Query(self._filter(*args, **kwargs))
