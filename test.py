#!/usr/bin/env python2
# encoding: utf-8

from nose.tools import *
from trek import *


def setup_module():
    Game.setup(3, 3)

def game_setup_test():
    assert_greater_equal(Game.bases, 1)
    assert_greater_equal(Game.klingons, 45)

class TestBaseValue:
    def setup(self):
        self.obj = BaseValue(item=42, test='Grayswandir')

    def initial_values_test(self):
        assert_equal(self.obj.item, 42)
        assert_equal(self.obj.item_base, 42)
        assert_equal(self.obj.test, 'Grayswandir')
        assert_equal(self.obj.test_base, 'Grayswandir')

    def changed_values_test(self):
        self.obj.item = 21
        self.obj.test = 'Jesus'
        assert_equal(self.obj.item, 21)
        assert_equal(self.obj.item_base, 42)
        assert_equal(self.obj.test, 'Jesus')
        assert_equal(self.obj.test_base, 'Grayswandir')


class TestGetSubclasses:
    class A(GetSubclasses):
        pass

    class B(A):
        pass

    class C(B):
        pass

    def get_subclasses_test(self):
        assert_sequence_equal(TestGetSubclasses.A.__subclasses__(), [TestGetSubclasses.B])
        sample = [TestGetSubclasses.B, TestGetSubclasses.C]
        assert_sequence_equal(TestGetSubclasses.A.get_subclasses(), sample)


class TestInstancesList:
    class A(InstancesList):
        pass

    class B(A):
        pass

    @classmethod
    def setup_class(cls):
        TestInstancesList.A(); TestInstancesList.A()
        TestInstancesList.B(); TestInstancesList.B(); TestInstancesList.B()

    @classmethod
    def teardown_class(cls):
        del TestInstancesList.A._instances[:]
        del TestInstancesList.B._instances[:]

    def instances_count_test(self):
        assert_equal(len(TestInstancesList.A._instances), 2)
        assert_equal(len(TestInstancesList.B._instances), 3)

    def get_instances_len_test(self):
        assert_equal(len(list(TestInstancesList.A.get_instances(children=False))), 2)
        assert_equal(len(list(TestInstancesList.B.get_instances(children=False))), 3)
        assert_equal(len(list(TestInstancesList.A.get_instances(children=True))), 5)


class TestWrappedColumn:
    class Object(WrappedColumn):
        array = 'data'
        size = 3

        def __init__(self):
            super(TestWrappedColumn.Object, self).__init__()
            self.data = list(range(9))

    def setup(self):
        self.obj = TestWrappedColumn.Object()

    def repr_test(self):
        assert_regexp_matches(repr(self.obj._column_wrapper), '<trek.ColumnWrapper around test.Object.data at .*>')

    def wrapper_instance_test(self):
        assert_is(self.obj[0], self.obj._column_wrapper)
        assert_is(self.obj[1], self.obj._column_wrapper)
        assert_is(self.obj[2], self.obj._column_wrapper)

    def data_retrieval_test(self):
        assert_equal(self.obj[0][0], 0)
        assert_equal(self.obj[0][1], 3)
        assert_equal(self.obj[1][1], 4)
        assert_equal(self.obj[2][2], 8)

    def data_modification_test(self):
        self.obj[0][2] = 42
        self.obj[1][0] = 21
        self.obj[2][1] = 84

        assert_sequence_equal(self.obj.data, [ 0, 21, 2,
                                               3, 4, 84,
                                              42, 7,  8])


class TestPrintableArray:
    class Object(PrintableArray):
        array = 'data'
        size = 3
        string_separator = '.'

        def __init__(self):
            super(TestPrintableArray.Object, self).__init__()
            self.data = list(range(9))

    def setup(self):
        self.obj = TestPrintableArray.Object()

    def get_string_test(self):
        sample = '0.1.2\n3.4.5\n6.7.8'
        assert_equal(self.obj.get_string(), sample)


class TestIteratorOnArray:
    class Object(IteratorOnArray):
        array = 'data'

        def __init__(self):
            super(TestIteratorOnArray.Object, self).__init__()
            self.data = list(range(9))

    def setup(self):
        self.obj = TestIteratorOnArray.Object()

    def iterator_test(self):
        i = iter(self.obj)
        i.next()
        assert_equal(i.next(), 1)

class TestQuery:
    @classmethod
    def setup_class(cls):
        cls.galaxy = Galaxy(4, 3)
        for quad in cls.galaxy:
            quad.setup()

        cls.quadrant = cls.galaxy[0][1]
        for sec in cls.quadrant:
            if sec._obj is not None:
                sec._obj._instances.remove(sec._obj)
                sec._obj = None

        cls.klingons = [Klingon(), Klingon(), Klingon()]

        cls.quadrant.get_sector().obj = cls.klingons[0]
        cls.quadrant.get_sector().obj = cls.klingons[1]
        cls.quadrant.get_sector().obj = cls.klingons[2]
        cls.quadrant.get_sector().obj = Base()
        cls.quadrant.get_sector().obj = Vessel(name='Vindicator', rep='Z')

        cls.sector = cls.quadrant.get_sector()
        cls.sector.obj = Enterprise()

    def found_objects_count_test(self):
        q = Query('Klingon')
        assert_equal(len(list(q)), len(Klingon._instances))

        q = Query('Vessel')
        assert_equal(len(list(q)), 1)

        q = Query('Vessel', subclasses=True)
        assert_equal(len(list(q)), 2)

        q = Query('Enterprise')
        assert_equal(len(list(q)), 1)

        q = Query('Klingon', quadrant=self.quadrant)
        assert_equal(len(list(q)), 3)

        q = Query('Vessel', sector=self.sector, subclasses=True)
        assert_equal(len(list(q)), 1)

        q = Query(quadrant=self.quadrant)
        assert_equal(len(list(q)), 6)

    def instances_test(self):
        assert_set_equal(set(Query(type='Klingon', quadrant=self.quadrant)), set(self.klingons))

    def chained_queries_test(self):
        assert_set_equal(set(Query(quadrant=self.quadrant).filter(type='Klingon')), set(self.klingons))

        q = Query(quadrant=self.quadrant)
        assert_is(q.filter('Vessel', subclasses=True).filter('Enterprise').get(), self.sector.obj)


class TestGalaxy:
    @classmethod
    def setup_class(cls):
        cls.galaxy = Galaxy(4, 3)
        for quad in cls.galaxy:
            quad.setup()

    def space_objects_count_test(self):
        assert_equal(len(Klingon._instances), Game.klingons)
        assert_equal(len(Base._instances), Game.bases)
