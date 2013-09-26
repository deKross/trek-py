# -*- coding: utf-8 -*-
import random


class Device(object):
    """
    Ship`s part.  A standalone system and base class for
    ship`s compartments.
    """
    def __init__(self, name, hp, probability):
        self.name = name
        self.max_hp, self.hp = hp, hp
        self.probability = probability / 100.0
        self.owner = None
        self._damaged = False

    def damage(self, probability, amount):
        if probability > self.probability:
            return False
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self._damaged = True
        return True

    def repair(self, amount):
        self.hp += amount
        if self.hp >= self.max_hp:
            self.hp = self.max_hp
            self._damaged = False
            return True
        return False

    @property
    def status(self):
        if self.owner._damaged:
            return 0.0
        if self._damaged:
            return float(self.hp) / float(self.max_hp)
        return 1.0


class Compartment(Device):
    def __init__(self, *a, **kw):
        super(Compartment, self).__init__(*a, **kw)
        self.devices = []
        self.issues = {"breaches": [], "fires": []}
        self.escape_pods = 0
        self.locked = False

    def add_device(self, device):
        self.devices.append(device)
        device.owner = self

    def sort_devices(self):
        temp = [(device.probability, device) for device in self.devices]
        temp.sort(reverse=True)
        self.devices = [entry[1] for entry in temp]

    def damage(self, probability, amount):
        if probability > self.probability:
            return False
