from .units import Unit, Weapon, WeaponType

from .abilities import (
    Ability, AutoHit, InvulnerableSave, HitModifier, MeltaRollDamageTwice, WoundReRollFailures, WoundReRoll, Resilient
)


# Death Guard-specific Abilities #

class DiseasedHorde(HitModifier):

    def __init__(self):
        super().__init__('Diseased Horde', 1)

    def active_prompt(self, attacking_unit, target_unit=None, aura_unit=None):
        return '{}: Does {} unit contain more than 10 models? '.format(self.name, attacking_unit.name)


# Common abilities #

disgustingly_resilient = Resilient('Disgustingly Resilient', 5)
plague_weapon = WoundReRoll('Plague Weapon', 1)
hit_minus_one = HitModifier('Subtract 1 from the hit roll', -1)


all_death_guard = [

    # DEATH GUARD #
    # DEATH GUARD ELITES #

    Unit('Blightlord Champion', 4, 3, 3, 4, 5, 2, 3, 9, 2, weapons=[
        Weapon('Combi-Bolter', 24, WeaponType.RAPID_FIRE, 2, 4, 0, 1),
        Weapon('Combi-Flamer (Boltgun)', 24, WeaponType.RAPID_FIRE, 1, 4, 0, 1),
        Weapon('Combi-Flamer (Flamer)', 8, WeaponType.ASSAULT, 'D6', 4, 0, 1),  # TODO autohit
        Weapon('Combi-Melta (Boltgun)', 24, WeaponType.RAPID_FIRE, 1, 4, 0, 1),
        Weapon('Combi-Melta (Meltagun)', 12, WeaponType.ASSAULT, 1, 8, -4, 'D6'),  # TODO melta
        Weapon('Combi-Plasma (Boltgun)', 24, WeaponType.RAPID_FIRE, 1, 4, 0, 1),
        Weapon('Combi-Plasma (Plasma Standard)', 24, WeaponType.RAPID_FIRE, 1, 7, -3, 1),
        Weapon('Combi-Plasma (Plasma Supercharged)', 24, WeaponType.RAPID_FIRE, 1, 8, -3, 2),
        Weapon('Balesword', None, WeaponType.MELEE, 'U', 'U', -3, 1, abilities=[plague_weapon]),
        Weapon('Bubotic Axe', None, WeaponType.MELEE, 'U', 'U+1', -2, 1, abilities=[plague_weapon]),
    ], abilities=[
        disgustingly_resilient,
        Ability('Teleport Strike'),
        InvulnerableSave('Cataphractii Armour', 4),
        Ability('Aura of Rust'),  # TODO make this ability
    ]),
    Unit('Blightlord Terminator', 4, 3, 3, 4, 5, 2, 2, 8, 2, weapons=[
        Weapon('Blight Launcher', 24, WeaponType.ASSAULT, 2, 6, -2, 'D3', abilities=[
            plague_weapon]),
        Weapon('Combi-Bolter', 24, WeaponType.RAPID_FIRE, 2, 4, 0, 1),
        Weapon('Combi-Flamer (Boltgun)', 24, WeaponType.RAPID_FIRE, 1, 4, 0, 1),
        Weapon('Combi-Flamer (Flamer)', 8, WeaponType.ASSAULT, 'D6', 4, 0, 1),  # TODO autohit
        Weapon('Combi-Melta (Boltgun)', 24, WeaponType.RAPID_FIRE, 1, 4, 0, 1),
        Weapon('Combi-Melta (Meltagun)', 12, WeaponType.ASSAULT, 1, 8, -4, 'D6'),  # TODO melta
        Weapon('Combi-Plasma (Boltgun)', 24, WeaponType.RAPID_FIRE, 1, 4, 0, 1),
        Weapon('Combi-Plasma (Plasma Standard)', 24, WeaponType.RAPID_FIRE, 1, 7, -3, 1),
        Weapon('Combi-Plasma (Plasma Supercharged)', 24, WeaponType.RAPID_FIRE, 1, 8, -3, 2),
        Weapon('Plague Spewer', 9, WeaponType.HEAVY, 'D6', 5, -1, 1, abilities=[plague_weapon, AutoHit()]),
        Weapon('Reaper Autocannon', 36, WeaponType.HEAVY, 4, 7, -1, 1),
        Weapon('Balesword', None, WeaponType.MELEE, 'U', 'U', -3, 1, abilities=[plague_weapon]),
        Weapon('Bubotic Axe', None, WeaponType.MELEE, 'U', 'U+1', -2, 1, abilities=[plague_weapon]),
        Weapon('Flail of Corruption', None, WeaponType.MELEE, 'D3', 'U+2', -2, 2, abilities=[plague_weapon]),  # TODO wound overflow
    ], abilities=[
        disgustingly_resilient,
        Ability('Teleport Strike'),
        InvulnerableSave('Cataphractii Armour', 4),
        Ability('Aura of Rust'),  # TODO make this ability
    ]),

    # DEATH GUARD FAST ATTACK #

    Unit('Foetid Bloat-drone', 10, 4, 4, 6, 7, 10, 3, 8, 3, weapons=[
        Weapon('Heavy Blight Launcher', 36, WeaponType.ASSAULT, 6, 6, -2, 'D3', abilities=[plague_weapon]),
        Weapon('Plague Spewer', 9, WeaponType.ASSAULT, 'D6', 'U', -1, 1, abilities=[plague_weapon, AutoHit()]),
        Weapon('Fleshmower', None, WeaponType.MELEE, 'U+6', 'U+2', -2, 2, abilities=[plague_weapon]),
        Weapon('Plague Probe', None, WeaponType.MELEE, 'U', 'U', -2, 'D3', abilities=[plague_weapon]),
    ], abilities=[
        disgustingly_resilient,
        InvulnerableSave('Daemonic', 5),
        Ability('Putrid Explosion')
    ]),

    # DEATH GUARD TROOPS #

    Unit('Plague Champion', 5, 3, 3, 4, 5, 1, 2, 8, 3, weapons=[
        Weapon('Bolt Pistol', 12, WeaponType.PISTOL, 1, 4, 0, 1),
        Weapon('Boltgun', 24, WeaponType.RAPID_FIRE, 1, 4, 0, 1),
        Weapon('Plasma Gun (Standard)', 24, WeaponType.RAPID_FIRE, 1, 7, -3, 1),
        Weapon('Plasma Gun (Supercharge)', 24, WeaponType.RAPID_FIRE, 1, 8, -3, 2),
        Weapon('Plasma Pistol (Standard)', 12, WeaponType.PISTOL, 1, 7, -3, 1),
        Weapon('Plasma Pistol (Supercharge)', 12, WeaponType.PISTOL, 1, 8, -3, 2),
        Weapon('Plague Knife', None, WeaponType.MELEE, 'U', 'U', 0, 1, abilities=[plague_weapon]),
        Weapon('Plague Sword', None, WeaponType.MELEE, 'U', 'U', 0, 1, abilities=[WoundReRollFailures()]),
        Weapon('Power Fist', None, WeaponType.MELEE, 'U', 'Ux2', -3, 'D3', abilities=[hit_minus_one]),
        Weapon('Blight Grenade', 6, WeaponType.GRENADE, 'D6', 3, 0, 1, abilities=[plague_weapon]),
        Weapon('Krak Grenade', 6, WeaponType.GRENADE, 1, 6, -1, 'D3'),
    ], abilities=[disgustingly_resilient]),
    Unit('Plague Marine', 5, 3, 3, 4, 5, 1, 2, 8, 3, weapons=[
        Weapon('Blight Launcher', 24, WeaponType.ASSAULT, 2, 6, -2, 'D3', abilities=[plague_weapon]),
        Weapon('Boltgun', 24, WeaponType.RAPID_FIRE, 1, 4, 0, 1),
        Weapon('Meltagun', 12, WeaponType.ASSAULT, 1, 8, -4, 'D6', abilities=[MeltaRollDamageTwice()]),
        Weapon('Plague Belcher', 9, WeaponType.ASSAULT, 'D6', 4, 0, 1, abilities=[plague_weapon, AutoHit()]),
        Weapon('Plague Spewer', 9, WeaponType.HEAVY, 'D6', 5, -1, 1, abilities=[plague_weapon, AutoHit()]),
        Weapon('Plasma Gun (Standard)', 24, WeaponType.RAPID_FIRE, 1, 7, -3, 1),
        Weapon('Plasma Gun (Supercharge)', 24, WeaponType.RAPID_FIRE, 1, 8, -3, 2),
        Weapon('Bubotic Axe', None, WeaponType.MELEE, 'U', 'U+1', -2, 1, abilities=[plague_weapon]),
        Weapon('Flail of Corruption', None, WeaponType.MELEE, 'D3', 'U+2', -2, 2, abilities=[plague_weapon]),  # TODO wound overflow
        Weapon('Great Plague Cleaver', None, WeaponType.MELEE, 'U', 'Ux2', -3, 'D6', abilities=[
            plague_weapon, hit_minus_one]),
        Weapon('Mace of Contagion', None, WeaponType.MELEE, 'U', 'U+2', -1, 3, abilities=[plague_weapon, hit_minus_one]),
        Weapon('Plague Knife', None, WeaponType.MELEE, 'U', 'U', 0, 1, abilities=[plague_weapon]),
        Weapon('Blight Grenade', 6, WeaponType.GRENADE, 'D6', 3, 0, 1, abilities=[plague_weapon]),
        Weapon('Krak Grenade', 6, WeaponType.GRENADE, 1, 6, -1, 'D3'),
    ], abilities=[disgustingly_resilient]),

    Unit('Poxwalker', 4, 5, 6, 3, 3, 1, 2, 4, 7, abilities=[disgustingly_resilient, DiseasedHorde()]),
]
