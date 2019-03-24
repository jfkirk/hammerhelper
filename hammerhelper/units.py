from enum import Enum

from abilities import AttacksModifier, InvulnerableSave, HitModifier, HitReRollAura


class WeaponType(Enum):
    MELEE = 1
    RAPID_FIRE = 2
    ASSAULT = 3
    HEAVY = 4
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
        for ability in self.abilities:
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

    def __init__(self, name, m, ws, bs, s, t, w, a, ld, sv, weapons, abilities=None):
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


all_units = [

    Unit('Captain in Gravis Armor', 5, 2, 2, 4, 5, 6, 5, 9, 3, weapons=[
        Weapon('Boltstorm Gauntlet (shooting)', 12, WeaponType.PISTOL, 3, 4, 0, 1),
        Weapon('Boltstorm Gauntlet (melee)', None, WeaponType.MELEE, 'U', 'Ux2', -3, 'D3', abilities=[
            HitModifier('Subtract 1 from the hit roll', -1)]),
        Weapon('Master-crafted Power Sword', None, WeaponType.MELEE, 'U', 'U', -3, 2),
    ], abilities=[
        InvulnerableSave('Iron Halo', 4),
        HitReRollAura('Rites of Battle', 1, 6),]),

    Unit('Intercessor Sergeant', 6, 3, 3, 4, 4, 2, 3, 8, 3, weapons=[
        Weapon('Auto Bolt Rifle', 30, WeaponType.ASSAULT, 2, 4, 0, 1),
        Weapon('Bolt Pistol', 12, WeaponType.PISTOL, 1, 4, 0, 1),
        Weapon('Bolt Rifle', 30, WeaponType.RAPID_FIRE, 1, 4, -1, 1),
        Weapon('Stalker Bolt Rifle', 36, WeaponType.HEAVY, 1, 4, -2, 1),
        Weapon('Chainsword', None, WeaponType.MELEE, 'U', 'U', 0, 1, abilities=[
            AttacksModifier('Each fight add one attack', 1)]),
        Weapon('Power Fist', None, WeaponType.MELEE, 'U', 'Ux2', -3, 'D3', abilities=[
            HitModifier('Subtract 1 from the hit roll', -1)]),
        Weapon('Power Sword', None, WeaponType.MELEE, 'U', 'U', -3, 1),
        Weapon('Frag Grenade', 6, WeaponType.GRENADE, 'D6', 3, 0, 1),
        Weapon('Krak Grenade', 6, WeaponType.GRENADE, 1, 6, -1, 'D3'),]),
    Unit('Intercessor', 6, 3, 3, 4, 4, 2, 2, 7, 3, weapons=[
        Weapon('Auto Bolt Rifle', 30, WeaponType.ASSAULT, 2, 4, 0, 1),
        Weapon('Bolt Pistol', 12, WeaponType.PISTOL, 1, 4, 0, 1),
        Weapon('Bolt Rifle', 30, WeaponType.RAPID_FIRE, 1, 4, -1, 1),
        Weapon('Stalker Bolt Rifle', 36, WeaponType.HEAVY, 1, 4, -2, 1),
        Weapon('Frag Grenade', 6, WeaponType.GRENADE, 'D6', 3, 0, 1),
        Weapon('Krak Grenade', 6, WeaponType.GRENADE, 1, 6, -1, 'D3'),]),

]
all_units_dict = {unit.name: unit for unit in all_units}
