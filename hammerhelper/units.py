from enum import Enum


class WeaponType(Enum):
    MELEE = 1
    RAPID_FIRE = 2
    ASSAULT = 3
    HEAVY = 4
    PISTOL = 5
    GRENADE = 6


class Weapon(object):

    def __init__(self, name, weapon_range, weapon_type, s, ap, d, abilities):
        self.name = name
        self.weapon_range = weapon_range
        self.weapon_type = weapon_type
        self.s = s
        self.ap = ap
        self.d = d

        if abilities:
            self.abilities = abilities
        else:
            self.abilities = []


default_melee = Weapon('Close Combat Weapon', None, WeaponType.MELEE, 'U', 0, 1, None)


class Unit(object):

    def __init__(self, name, m, ws, bs, s, t, w, a, ld, sv, weapons, abilities):
        self.name = name
        self.m = m
        self.ws = ws
        self.bs = bs
        self.s = s
        self.t = t
        self.w = w
        self.a = a
        self.ld = ld
        self.sv = sv

        if weapons:
            self.weapons = weapons
        else:
            self.weapons = []
        self.weapons.append(default_melee)

        if abilities:
            self.abilities = abilities
        else:
            self.abilities = []


all_units = [
    Unit('Intercessor', 6, 3, 3, 4, 4, 2, 2, 7, 3, weapons=[
        Weapon('Bolt Rifle', 30, WeaponType.RAPID_FIRE, 4, -1, 1, None)
    ], abilities=None),
]
all_units_dict = {unit.name: unit for unit in all_units}