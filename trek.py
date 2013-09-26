#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import math
import random
import itertools


class BaseValue(object):
    """Save current and base values"""

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            self.set(key, value)

    def set(self, name, value):
        setattr(self, name, value)
        setattr(self, name + '_base', value)


class Game:
    skill = length = bases_base = bases = time_base = time = klingons_base = klingons = \
    resources_base = resources = date_base = date = 0
    klingon_power = 0

    max_klingons_in_quadrant = 9

    @classmethod
    def setup(cls, skill, length):
        cls.skill = skill
        cls.length = length

        if skill == 6:
            cls.bases_base = cls.bases = 1
        else:
            cls.bases_base = cls.bases = random.randint(0, 6 - skill) + 2

        cls.time_base = cls.time = 6.0 * length + 2.0

        cls.klingons_base = cls.klingons = int(skill * length * 3.5 * (random.random() + 0.75))
        if cls.klingons < skill * length * 5:
            cls.klingons_base = cls.klingons = skill * length * 5

        cls.klingon_power = 100 + 150 * skill
        if skill >= 6:
            cls.klingon_power += 150

        cls.resources_base = cls.resources = cls.klingons * cls.time
        cls.date_base = cls.date = (random.randint(0, 20) + 20) * 100


class Point(object):
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "%d, %d" % (self.x, self.y)

    def set(self, *args):
        self.x, self.y = args


class VesselDevice(object):
    def __init__(self, name, fac, prob):
        self.name = name
        self.fac = 0 if name[0] == '*' else fac
        self.probability = prob

    @property
    def damaged(self):
        return False


class GetSubclasses(object):
    @classmethod
    def get_subclasses(cls):
        result = cls.__subclasses__()

        for scls in cls.__subclasses__():
            result.extend(scls.get_subclasses())

        return result


class InstancesList(GetSubclasses):
    def __init__(self):
        inst = self.__class__.__dict__.get('_instances')
        if inst is None:
            inst = []
            setattr(self.__class__, '_instances', inst)
        inst.append(self)

    @classmethod
    def get_instances(cls, children=False):
        if cls.__dict__.get('_instances') is None:
            result = iter([])
        else:
            result = iter(cls._instances)

        if not children:
            return result

        for scls in cls.__subclasses__():
            result = itertools.chain(result, scls.get_instances(children=True))

        return result


class SpaceObject(InstancesList):
    representation = ' '

    def __init__(self):
        super(SpaceObject, self).__init__()

        self._sector = None

    def __str__(self):
        return self.representation

    @property
    def quadrant(self):
        return self._sector.quadrant if self._sector is not None else None

    @property
    def sector(self):
        return self._sector

    @sector.setter
    def sector(self, sec):
        sec.obj = self


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

    def get(self):
        if self.queryset:
            return self.queryset[0]
        return 0

    def _filter(self, *args, **kwargs):
        types = []
        for arg in args:
            types.extend(arg.split())
        arg = kwargs.get('type')
        if arg is not None:
            types.extend(arg.split())

        if types:
            types = [cls for cls in SpaceObject.get_subclasses() if cls.__name__ in types]
            #if kwargs.get('subclasses'):
                #super_types = list(types)
                #for cls in super_types:
                    #types.extend(cls.get_subclasses())
                #types = list(set(types))

        quadrant_check = lambda quad: True
        sector_check = lambda sec: True
        object_check = lambda obj: True

        sector = kwargs.get('sector')
        if sector is not None:
            if isinstance(sector, (list, tuple)):
                sector_check = lambda sec: sec in sector
            else:
                sector_check = lambda sec: sec is sector
        else:
            quadrant = kwargs.get('quadrant')
            if quadrant is not None:
                if isinstance(quadrant, (list, tuple)):
                    quadrant_check = lambda quad: quad in quadrant
                else:
                    quadrant_check = lambda quad: quad is quadrant

        if self.queryset:
            data = self.queryset
            if types:
                if kwargs.get('subclasses'):
                    super_types = list(types)
                    for cls in super_types:
                        types.extend(cls.get_subclasses())
                types = set(types)
                object_check = lambda obj: type(obj) in types
        else:
            if types:
                data = itertools.chain.from_iterable(cls.get_instances(kwargs.get('subclasses', False)) for cls in types)
            else:
                data = itertools.chain.from_iterable(cls.get_instances() for cls in SpaceObject.get_subclasses())

        result = [obj for obj in data if
                  quadrant_check(obj.quadrant) and sector_check(obj.sector) and object_check(obj)]

        return result

    def filter(self, *args, **kwargs):
        return Query(self._filter(*args, **kwargs))


class Vessel(SpaceObject, BaseValue):
    GREEN = 0
    RED = 1

    def __init__(self, name, rep, **kwargs):
        self.name, self.representation = name, rep
        self.energy = self.torpedoes = self.shield = self.crew = self.brig_free = self.reserves = 0
        self.warp_one = 0
        self.devices = []
        SpaceObject.__init__(self)
        BaseValue.__init__(self, **kwargs)

    def add_device(self, **kwargs):
        device = VesselDevice(**kwargs)
        self.devices.append(VesselDevice(**kwargs))

        name = kwargs['name']
        if isinstance(name, (tuple, list)):
            device.name = name[0]
            name = name[1]

        name = name.lower().replace(' ', '_')
        name = 'dev_' + name
        setattr(self, name, device)

    def check_enemies(self):
        raise NotImplemented

    def get_warp(self, factor):
        return self.warp_one ** factor

    def move_to_quadrant(self, quadrant, f):
        self.quadrant = quadrant

        if quadrant.stars < 0:
            return

        if not f and self.check_enemies():
            self.condition = Vessel.RED
            if not self.dev_computer.damaged:
                self.shield(True)


class Enterprise(Vessel):
    def __init__(self):
        super(Enterprise, self).__init__('Enterprise', 'E',
                                        energy=5000, torpedoes=10, shield=1500,
                                        crew=387, brig_free=400)
        self.shield_up = True
        self.condition = Vessel.GREEN
        self.sins_bad = False
        self.cloaked = False
        self.warp_one = 5.0
        self.set('reserves', (6 - Game.skill) * 2.0)

        names = ('Warp engines', 'Short range scanners', 'Long range scanners',
                 'Phaser control', 'Photon torpedo control', 'Impulse engines',
                 'Shield control', ('On board computer', 'computer'), 'Subspace radio',
                 'Life support systems', ('Space inertial navigation system', 'sins'),
                 'Cloaking device', 'Transporter')
        probs = (70, 110, 110, 125, 125, 75, 150, 20, 35, 30, 20, 50, 80)
        if sum(probs) != 1000: raise ValueError("Device probabilities %s is not equals to 1000" % sum(probs))
        f = math.log(Game.skill + 0.5)
        for i in range(len(names)):
            self.add_device(name=names[i], fac=f, prob=probs[i])
        self.add_device(name='Shuttlecraft', fac=0, prob=0)

    def check_enemies(self):
        return self.quadrant.klingons > 0


class Klingon(SpaceObject):
    representation = 'K'


class Base(SpaceObject):
    representation = '#'


class BlackHole(SpaceObject):
    representation = ' '


class Star(SpaceObject):
    representation = '*'


class Inhabited(Star):
    representation = '@'


class Sector(object):
    representation = '.'

    __slots__ = ('x', 'y', 'quadrant', '_obj')

    def __init__(self, x, y, quadrant):
        super(Sector, self).__init__()
        self.x, self.y = x, y
        self.quadrant = quadrant
        self._obj = None

    def __str__(self):
        if self._obj:
            return str(self._obj)
        return self.representation

    @property
    def empty(self):
        return self._obj is None

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, o):
        if o._sector is not None:
            o._sector._obj = None
        o._sector = self
        self._obj = o


class WrappedColumn(object):
    class ColumnWrapper(object):
        def __init__(self, target):
            self.target = target
            self.index = 0

        def __repr__(self):
            return "<%s.%s around %s.%s.%s at %s>" % (
                self.__module__,
                self.__class__.__name__,
                self.target.__module__,
                self.target.__class__.__name__,
                self.target.array,
                hex(id(self)))

        def __getitem__(self, index):
            return getattr(self.target, self.target.array)[self.target.size * index + self.index]

        def __setitem__(self, index, value):
            getattr(self.target, self.target.array)[self.target.size * index + self.index] = value


    def __init__(self):
        self._column_wrapper = WrappedColumn.ColumnWrapper(self)

    def __getitem__(self, index):
        self._column_wrapper.index = index
        return self._column_wrapper


class PrintableArray(object):
    string_separator = ''
    top_border = ''
    bottom_border = ''
    left_border = ''
    right_border = ''

    def get_strings(self):
        array = getattr(self, self.array)
        s = self.size
        return tuple(self.string_separator.join(str(array[s * y + x]) for x in xrange(s)) for y in xrange(s))

    def get_string(self):
        return '\n'.join(self.get_strings())


class IteratorOnArray(object):
    def __iter__(self):
        return iter(getattr(self, self.array, ()))


class Quadrant(WrappedColumn, InstancesList, PrintableArray, IteratorOnArray):
    size = 10
    array = 'sectors'
    string_separator = ' '

    def __init__(self):
        WrappedColumn.__init__(self)
        InstancesList.__init__(self)

        self.klingons = 0
        self.base = None
        self.scanned = -1
        self.stars = random.randint(0, 9) + 1
        self.holes = random.randint(0, 3) - self.stars // 5
        self.system_name = ''
        self.sectors = [Sector(i % self.size, i // self.size, self) for i in xrange(self.size ** 2)]

    def get_sector(self):
        while True:
            sector = random.choice(self.sectors)
            if sector.empty:
                return sector

    def setup(self):
        for i in xrange(self.klingons):
            sector = self.get_sector()
            klingon = Klingon()
            klingon.power = Game.klingon_power
            klingon.surround_req = 0
            sector.obj = klingon

        if self.base:
            self.get_sector().obj = self.base

        for i in xrange(self.holes):
            self.get_sector().obj = BlackHole()

        nstars = self.stars

        if self.system_name:
            self.get_sector().obj = Inhabited()
            nstars -= 1

        for i in xrange(nstars):
            self.get_sector().obj = Star()

        del self.klingons
        del self.stars
        del self.holes


class Galaxy(WrappedColumn, InstancesList, PrintableArray, IteratorOnArray):
    array = 'quads'

    def __init__(self, quads, inhab):
        WrappedColumn.__init__(self)
        InstancesList.__init__(self)

        self.size = quads
        self.quads = tuple(Quadrant() for i in xrange(quads ** 2))

        system_names = ['Talos IV', 'Rigel III', 'Deneb VIII', 'Canopus V', 'Icarus I', 'Prometheus II',
                        'Omega VII', 'Elysium I', 'Scalos IV', 'Procyon IV', 'Arachnid I', 'Argo VIII',
                        'Triad III', 'Echo IV', 'Nimrod III', 'Nemisis IV', 'Centarurus I', 'Kronos III',
                        'Specros V', 'Beta III', 'Gamma Tranguli VI', 'Pyris III', 'Triachus', 'Marcus XII',
                        'Kaland', 'Ardana', 'Stratos', 'Eden', 'Arrikis', 'Epsilon Eridani IV', 'Exo III']
        system_names = random.sample(system_names, inhab)
        inhab_systems = random.sample(self.quads, inhab)
        for quad in inhab_systems:
            quad.system_name = system_names.pop()

        base_systems = random.sample(self.quads, Game.bases)
        for system in base_systems:
            system.base = Base()
            system.scanned = 1001

        i = Game.klingons
        while i > 0:
            klump = min(random.randint(1, 5), i)
            while True:
                quad = random.choice(self.quads)
                if quad.klingons + klump > Game.max_klingons_in_quadrant:
                    continue
                quad.klingons += klump
                i -= klump
                break

    def get_all_quadrants_string(self):
        result = []
        for i in xrange(len(self.quads) / self.size):
            row = []
            index = i * self.size
            quads = self.quads[index:index + self.size]
            strings = [quad.get_strings() for quad in quads]
            for j in xrange(Quadrant.size):
                result.append(Quadrant.string_separator.join(quad[j] for quad in strings))
        return '\n'.join(result)


gal = None
def main():
    global gal
    Game.setup(3, 3)
    gal = Galaxy(4, 3)
    for q in gal:
        q.setup()

if __name__ == '__main__':
    main()
