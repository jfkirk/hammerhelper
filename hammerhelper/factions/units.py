from enum import Enum

from .abilities import sort_abilities


class WeaponType(Enum):
    MELEE = 1
    RAPID_FIRE = 2
    ASSAULT = 3  # TODO prompt + penalty for assault weapons?
    HEAVY = 4  # TODO prompt + penalty for heavy weapons?
    PISTOL = 5
    GRENADE = 6


class Weapon(object):

    def __init__(self, name, weapon_range, weapon_type, a, s, ap, d, abilities=None):
        self.name = name
        self.weapon_range = weapon_range
        self.weapon_type = weapon_type
        self.a = a
        self.s = s
        self.ap = ap
        self.d = d

        if abilities:
            self.abilities = abilities
        else:
            self.abilities = []

    @property
    def offensive_abilities(self):
        return [ab for ab in self.abilities if ab.offensive]

    @property
    def offensive_targeted_abilities(self):
        return [ab for ab in self.abilities if ab.offensive_targeted]

    def effective_attacks(self, unit):
        if self.a == 'U':
            result = unit.a
        else:
            result = self.a
        for ability in sort_abilities(self.abilities, 'modify_effective_attacks'):
            result = ability.modify_effective_attacks(result)
        return result

    def effective_strength(self, unit):
        if self.s == 'U':
            return unit.s
        if 'Ux' in str(self.s):
            multplier = int(self.s[2:])
            return multplier * unit.s
        # TODO handle multiples
        return self.s


default_melee = Weapon('Close Combat Weapon', None, WeaponType.MELEE, 'U', 'U', 0, 1, None)


class Unit(object):

    def __init__(self, name, m, ws, bs, s, t, w, a, ld, sv, weapons=None, abilities=None):
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

    @property
    def offensive_abilities(self):
        return [ab for ab in self.abilities if (not ab.aura and ab.offensive)]

    @property
    def offensive_targeted_abilities(self):
        return [ab for ab in self.abilities if ab.offensive_targeted]

    @property
    def defensive_abilities(self):
        return [ab for ab in self.abilities if ab.defensive]

    @property
    def offensive_auras(self):
        return [ab for ab in self.abilities if (ab.aura and ab.offensive)]

    @property
    def offensive_targeted_auras(self):
        return [ab for ab in self.abilities if (ab.aura and ab.offensive_targeted)]

    @property
    def defensive_auras(self):
        return [ab for ab in self.abilities if (ab.aura and ab.defensive)]