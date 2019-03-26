import numpy as np
from distutils.util import strtobool


def string_from_ability_list(abilities):
    result = ''
    for i, ability in enumerate(abilities):
        result += '{}'.format(ability.name)
        if i < len(abilities) - 1:
            result += ', '
    return result


def boolean_prompt(text):
    result = None
    while result is None:
        try:
            response = input(text)
            result = strtobool(response)
        except ValueError:
            print('Invalid response "{}", try "T" or "F"'.format(response))
    return result


class Ability(object):
    # If True, this is a unit ability that has an effect when the unit is attacking any target
    offensive = False

    # If True, this offensive ability only applies to specific attack targets
    offensive_targeted = False

    # If True, this is a unit ability that has an effect when the unit is being attacked
    defensive = False

    # If True, this ability may effect other units
    aura = False

    # A higher 'order' value ability will take effect later than an ability with a lower 'order' value
    order = 1

    def __init__(self, name):
        self.name = name

    def is_active_prompt(self, attacking_unit, target_unit=None, aura_unit=None):
        return True

    def modify_effective_attacks(self, effective_attacks):
        return effective_attacks

    def modify_hit_rolls(self, hit_rolls, hit_target):
        return hit_rolls

    def modify_wound_rolls(self, wound_rolls):
        return wound_rolls

    def modify_save_rolls(self, save_rolls):
        return save_rolls

    def modify_save_target(self, save_target):
        return save_target

    def modify_damage_rolls(self, damage_rolls):
        return damage_rolls


class InvulnerableSave(Ability):
    defensive = True

    def __init__(self, name, value):
        super().__init__(name)
        self.value = value

    def modify_save_target(self, save_target):
        if save_target >= self.value:
            return self.value
        return save_target


class AttacksModifier(Ability):

    def __init__(self, name, modifier):
        super().__init__(name)
        self.modifier = modifier

    def modify_effective_attacks(self, effective_attacks):
        return effective_attacks + self.modifier


class HitModifier(Ability):
    offensive = True
    order = 2  # Modifiers take effect after rerolls

    def __init__(self, name, modifier):
        super().__init__(name)
        self.modifier = modifier

    def modify_hit_rolls(self, hit_rolls, hit_target):
        return hit_rolls + self.modifier


class AutoHit(Ability):
    offensive = True
    order = 3  # Go after all other hit mods

    def modify_hit_rolls(self, hit_rolls, hit_target):
        hit_rolls.fill(hit_target + 1)  # The +1 is just for my sanity
        return hit_rolls


class HitReRollAura(Ability):
    offensive = True
    aura = True

    def __init__(self, name, value, aura_range):
        super().__init__(name)
        self.value = value
        self.aura_range = aura_range

    def is_active_prompt(self, attacking_unit, target_unit=None, aura_unit=None):
        if attacking_unit == aura_unit:
            return True
        return boolean_prompt('{}: Is {} within {}" of {}? '.format(self.name, attacking_unit.name, self.aura_range, aura_unit.name))

    def modify_hit_rolls(self, hit_rolls, hit_target):
        failed_rolls = np.argwhere(hit_rolls <= self.value)
        reroll = np.random.randint(1, 6, size=len(failed_rolls))
        for i, failed_roll_loc in enumerate(failed_rolls):
            hit_rolls[failed_roll_loc] = reroll[i]
        return hit_rolls


class WoundReRollAura(Ability):
    offensive = True
    aura = True

    def __init__(self, name, value, aura_range):
        super().__init__(name)
        self.value = value
        self.aura_range = aura_range

    def is_active_prompt(self, attacking_unit, target_unit=None, aura_unit=None):
        if attacking_unit == aura_unit:
            return True
        return boolean_prompt('{}: Is {} within {}" of {}? '.format(self.name, attacking_unit.name, self.aura_range, aura_unit.name))

    def modify_wound_rolls(self, wound_rolls):
        failed_rolls = np.argwhere(wound_rolls <= self.value)
        reroll = np.random.randint(1, 6, size=len(failed_rolls))
        for i, failed_roll_loc in enumerate(failed_rolls):
            wound_rolls[failed_roll_loc] = reroll[i]
        return wound_rolls
