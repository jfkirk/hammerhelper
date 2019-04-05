from enum import Enum

from abilities import (sort_abilities, Ability, AttacksModifier, DiseasedHorde, InvulnerableSave, AutoHit, HitModifier,
                       HitReRollAura, Resilient, WoundReRoll, WoundReRollAura)


class WeaponType(Enum):
    MELEE = 1
    RAPID_FIRE = 2
    ASSAULT = 3  # TODO prompt + penalty for assault weapons?
    HEAVY = 4  # TODO prompt + penalty for assault weapons?
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


all_units = [

    # DEATH GUARD #
    # DEATH GUARD TROOPS #

    Unit('Plague Champion', 5, 3, 3, 4, 5, 1, 2, 8, 3, weapons=[
        Weapon('Blight Launcher', 24, WeaponType.ASSAULT, 2, 6, -2, 'D3', abilities=[WoundReRoll('Plague Weapon', 1)]),
        Weapon('Bolt Pistol', 12, WeaponType.PISTOL, 1, 4, 0, 1),
        Weapon('Boltgun', 24, WeaponType.RAPID_FIRE, 1, 4, 0, 1),
        Weapon('Meltagun', 12, WeaponType.ASSAULT, 1, 8, -4, 'D6'),  # TODO roll two damage dice ability
        Weapon('Plague Belcher', 9, WeaponType.ASSAULT, 'D6', 4, 0, 1),  # TODO autohit, plague weapon
        Weapon('Plague Spewer', 9, WeaponType.HEAVY, 'D6', 5, -1, 1),  # TODO autohit, plague weapon
        Weapon('Plasma Gun (Standard)', 24, WeaponType.RAPID_FIRE, 1, 7, -3, 1),
        Weapon('Plasma Gun (Supercharge)', 24, WeaponType.RAPID_FIRE, 1, 8, -3, 2),
        Weapon('Plasma Pistol (Standard)', 12, WeaponType.PISTOL, 1, 7, -3, 1),
        Weapon('Plasma Pistol (Supercharge)', 12, WeaponType.PISTOL, 1, 8, -3, 2),
        Weapon('Bubotic Axe', None, WeaponType.MELEE, 'U', 'U+1', -2, 1),  # TODO plague weapon
        Weapon('Flail of Corruption', None, WeaponType.MELEE, 'D3', 'U+2', -2, 2),  # TODO plague weapon, wound overflow
        Weapon('Great Plague Cleaver', None, WeaponType.MELEE, 'U', 'Ux2', -3, 'D6'),  # TODO plague weapon, hit penalty
        Weapon('Mace of Contagion', None, WeaponType.MELEE, 'U', 'U+2', -1, 3),  # TODO plague weapon, hit penalty
        Weapon('Plague Knife', None, WeaponType.MELEE, 'U', 'U', 0, 1),  # TODO plague weapon
        Weapon('Plague Sword', None, WeaponType.MELEE, 'U', 'U', 0, 1),  # TODO reroll FAILED wound rolls
        Weapon('Power Fist', None, WeaponType.MELEE, 'U', 'Ux2', -3, 'D3'),  # TODO hit penalty
        Weapon('Blight Grenade', 6, WeaponType.GRENADE, 'D6', 3, 0, 1),  # TODO plague weapon
        Weapon('Krak Grenade', 6, WeaponType.GRENADE, 1, 6, -1, 'D3'),
    ], abilities=[Resilient('Disgustingly Resilient', 5)]),

    Unit('Poxwalker', 4, 5, 6, 3, 3, 1, 2, 4, 7, abilities=[
        Resilient('Disgustingly Resilient', 5),
        DiseasedHorde(),
    ]),

    # SPACE MARINES #
    # SPACE MARINE HQ #

    Unit('Captain in Gravis Armor', 5, 2, 2, 4, 5, 6, 5, 9, 3, weapons=[
        Weapon('Boltstorm Gauntlet (shooting)', 12, WeaponType.PISTOL, 3, 4, 0, 1),
        Weapon('Boltstorm Gauntlet (melee)', None, WeaponType.MELEE, 'U', 'Ux2', -3, 'D3', abilities=[
            HitModifier('Subtract 1 from the hit roll', -1)]),
        Weapon('Master-crafted Power Sword', None, WeaponType.MELEE, 'U', 'U', -3, 2),
    ], abilities=[InvulnerableSave('Iron Halo', 4),
                  HitReRollAura('Rites of Battle', 1, 6)]),

    Unit('Primaris Lieutenant', 6, 2, 3, 4, 4, 5, 4, 8, 3, weapons=[
        Weapon('Bolt Pistol', 12, WeaponType.PISTOL, 1, 4, 0, 1),
        Weapon('Master-crafted Auto Bolt Rifle', 24, WeaponType.ASSAULT, 2, 4, 0, 2),
        Weapon('Master-crafted Stalker Bolt Rifle', 36, WeaponType.HEAVY, 1, 4, -2, 2),
        Weapon('Power Sword', None, WeaponType.MELEE, 'U', 'U', -3, 1),
        Weapon('Frag Grenade', 6, WeaponType.GRENADE, 'D6', 3, 0, 1),
        Weapon('Krak Grenade', 6, WeaponType.GRENADE, 1, 6, -1, 'D3'),
    ], abilities=[WoundReRollAura('Tactical Precision', 1, 6)]),

    # SPACE MARINE ELITES #

    Unit('Aggressor Sergeant', 5, 3, 3, 4, 5, 2, 2, 8, 3, weapons=[
        Weapon('Auto Boltstorm Gauntlets (Shooting)', 18, WeaponType.ASSAULT, 6, 4, 0, 1),
        Weapon('Flamestorm Gauntlets (Shooting)', 8, WeaponType.ASSAULT, '2D6', 4, 0, 1, abilities=[
            AutoHit('This weapon automatically hits its target')]),
        Weapon('Fragstorm Grenade Launcher', 18, WeaponType.ASSAULT, 'D6', 4, 0, 1),
        Weapon('Auto Boltstorm Gauntlets (Melee)', None, WeaponType.MELEE, 'U', 'Ux2', -3, 'D3', abilities=[
            HitModifier('Subtract 1 from the hit roll', -1)]),
        Weapon('Flamestorm Gauntlets (Melee)', None, WeaponType.MELEE, 'U', 'Ux2', -3, 'D3', abilities=[
            HitModifier('Subtract 1 from the hit roll', -1)]),
    ], abilities=[Ability('Fire Storm')]),  # TODO prompt before shots?
    Unit('Aggressor', 5, 3, 3, 4, 5, 2, 2, 7, 3, weapons=[
        Weapon('Auto Boltstorm Gauntlets (Shooting)', 18, WeaponType.ASSAULT, 6, 4, 0, 1),
        Weapon('Flamestorm Gauntlets (Shooting)', 8, WeaponType.ASSAULT, '2D6', 4, 0, 1, abilities=[
            AutoHit('This weapon automatically hits its target')]),
        Weapon('Fragstorm Grenade Launcher', 18, WeaponType.ASSAULT, 'D6', 4, 0, 1),
        Weapon('Auto Boltstorm Gauntlets (Melee)', None, WeaponType.MELEE, 'U', 'Ux2', -3, 'D3', abilities=[
            HitModifier('Subtract 1 from the hit roll', -1)]),
        Weapon('Flamestorm Gauntlets (Melee)', None, WeaponType.MELEE, 'U', 'Ux2', -3, 'D3', abilities=[
            HitModifier('Subtract 1 from the hit roll', -1)]),
    ], abilities=[Ability('Fire Storm')]),  # TODO prompt before shots?

    Unit('Primaris Ancient', 6, 3, 3, 4, 4, 5, 4, 8, 3, weapons=[
        Weapon('Bolt Pistol', 12, WeaponType.PISTOL, 1, 4, 0, 1),
        Weapon('Bolt Rifle', 30, WeaponType.RAPID_FIRE, 1, 4, -1, 1),
        Weapon('Frag Grenade', 6, WeaponType.GRENADE, 'D6', 3, 0, 1),
        Weapon('Krak Grenade', 6, WeaponType.GRENADE, 1, 6, -1, 'D3')
    ], abilities=[Ability('Astartes Banner')]),

    Unit('Primaris Apothecary', 6, 3, 3, 4, 4, 5, 3, 8, 3, weapons=[
        Weapon('Absolver Bolt Pistol', 16, WeaponType.PISTOL, 1, 5, -1, 1),
        Weapon('Reductor Pistol', 3, WeaponType.PISTOL, 1, 4, -3, 2),
        Weapon('Frag Grenade', 6, WeaponType.GRENADE, 'D6', 3, 0, 1),
        Weapon('Krak Grenade', 6, WeaponType.GRENADE, 1, 6, -1, 'D3')
    ], abilities=[Ability('Narthecium')]),

    Unit('Redemptor Dreadnaught', 8, 3, 3, 7, 7, 13, 4, 8, 3, weapons=[
        Weapon('Macro Plasma Incinerator (Standard)', 36, WeaponType.HEAVY, 'D6', 8, -4, 1),
        Weapon('Macro Plasma Incinerator (Supercharge)', 36, WeaponType.HEAVY, 'D6', 9, -4, 2),
        Weapon('Heavy Onslaught Gatling Cannon', 30, WeaponType.HEAVY, 12, 5, -1, 1),
        Weapon('Heavy Flamer', 8, WeaponType.HEAVY, 'D6', 5, -1, 1),  # TODO autohit
        Weapon('Onslaught Gatling Cannon', 24, WeaponType.HEAVY, 6, 5, -1, 1),
        Weapon('Storm Bolter', 24, WeaponType.RAPID_FIRE, 2, 4, 0, 1),
        Weapon('Fragstorm Grenade Launcher', 18, WeaponType.ASSAULT, 'D6', 4, 0, 1),
        Weapon('Icarus Rocket Pod', 24, WeaponType.HEAVY, 'D3', 7, -1, 1),  # TODO anti-air
        Weapon('Redemptor Fist', None, WeaponType.MELEE, 'U', 'Ux2', -3, 'D6'),
    ], abilities=[Ability('Explodes')]),

    # SPACE MARINE FAST ATTACK #

    Unit('Inceptor Sergeant', 10, 3, 3, 4, 5, 2, 2, 8, 3, weapons=[
        Weapon('Assault Bolter', 18, WeaponType.ASSAULT, 3, 5, -1, 1),
        Weapon('Plasma Exterminator (Standard)', 18, WeaponType.ASSAULT, 'D3', 7, -3, 1),
        Weapon('Plasma Exterminator (Supercharge)', 18, WeaponType.ASSAULT, 'D3', 8, -3, 2)
    ], abilities=[Ability('Meteoric Descent'),
                  Ability('Crushing Charge')]),
    Unit('Inceptor', 10, 3, 3, 4, 5, 2, 2, 7, 3, weapons=[
        Weapon('Assault Bolter', 18, WeaponType.ASSAULT, 3, 5, -1, 1),
        Weapon('Plasma Exterminator (Standard)', 18, WeaponType.ASSAULT, 'D3', 7, -3, 1),
        Weapon('Plasma Exterminator (Supercharge)', 18, WeaponType.ASSAULT, 'D3', 8, -3, 2)
    ], abilities=[Ability('Meteoric Descent'),
                  Ability('Crushing Charge')]),

    # SPACE MARINE HEAVY SUPPORT #

    Unit('Hellblaster Sergeant', 6, 3, 3, 4, 4, 2, 2, 7, 3, weapons=[
        Weapon('Assault Plasma Incinerator (Standard)', 24, WeaponType.ASSAULT, 2, 6, -4, 1),
        Weapon('Assault Plasma Incinerator (Supercharge)', 24, WeaponType.ASSAULT, 2, 7, -4, 2),
        Weapon('Heavy Plasma Incinerator (Standard)', 36, WeaponType.HEAVY, 1, 8, -4, 1),
        Weapon('Heavy Plasma Incinerator (Supercharge)', 36, WeaponType.HEAVY, 1, 9, -4, 2),
        Weapon('Plasma Incinerator (Standard)', 30, WeaponType.RAPID_FIRE, 1, 7, -4, 1),
        Weapon('Plasma Incinerator (Supercharge)', 30, WeaponType.RAPID_FIRE, 1, 8, -4, 2),
        Weapon('Bolt Pistol', 12, WeaponType.PISTOL, 1, 4, 0, 1),
        Weapon('Frag Grenade', 6, WeaponType.GRENADE, 'D6', 3, 0, 1),
        Weapon('Krak Grenade', 6, WeaponType.GRENADE, 1, 6, -1, 'D3')]),
    Unit('Hellblaster', 6, 3, 3, 4, 4, 2, 2, 7, 3, weapons=[
        Weapon('Assault Plasma Incinerator (Standard)', 24, WeaponType.ASSAULT, 2, 6, -4, 1),
        Weapon('Assault Plasma Incinerator (Supercharge)', 24, WeaponType.ASSAULT, 2, 7, -4, 2),
        Weapon('Heavy Plasma Incinerator (Standard)', 36, WeaponType.HEAVY, 1, 8, -4, 1),
        Weapon('Heavy Plasma Incinerator (Supercharge)', 36, WeaponType.HEAVY, 1, 9, -4, 2),
        Weapon('Plasma Incinerator (Standard)', 30, WeaponType.RAPID_FIRE, 1, 7, -4, 1),
        Weapon('Plasma Incinerator (Supercharge)', 30, WeaponType.RAPID_FIRE, 1, 8, -4, 2),
        Weapon('Plasma Pistol (Standard)', 12, WeaponType.PISTOL, 1, 7, -3, 1),
        Weapon('Plasma Pistol (Supercharge)', 12, WeaponType.PISTOL, 1, 8, -3, 2),
        Weapon('Bolt Pistol', 12, WeaponType.PISTOL, 1, 4, 0, 1),
        Weapon('Frag Grenade', 6, WeaponType.GRENADE, 'D6', 3, 0, 1),
        Weapon('Krak Grenade', 6, WeaponType.GRENADE, 1, 6, -1, 'D3')]),

    # SPACE MARINE TROOPS #

    Unit('Intercessor Sergeant', 6, 3, 3, 4, 4, 2, 3, 8, 3, weapons=[
        Weapon('Auto Bolt Rifle', 24, WeaponType.ASSAULT, 2, 4, 0, 1),
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
        Weapon('Auto Bolt Rifle', 24, WeaponType.ASSAULT, 2, 4, 0, 1),
        Weapon('Bolt Pistol', 12, WeaponType.PISTOL, 1, 4, 0, 1),
        Weapon('Bolt Rifle', 30, WeaponType.RAPID_FIRE, 1, 4, -1, 1),
        Weapon('Stalker Bolt Rifle', 36, WeaponType.HEAVY, 1, 4, -2, 1),
        Weapon('Frag Grenade', 6, WeaponType.GRENADE, 'D6', 3, 0, 1),
        Weapon('Krak Grenade', 6, WeaponType.GRENADE, 1, 6, -1, 'D3')]),

]
all_units_dict = {unit.name: unit for unit in all_units}
