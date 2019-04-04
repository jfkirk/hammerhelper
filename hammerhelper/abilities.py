import numpy as np


def string_from_ability_list(abilities):
    result = ''
    for i, ability in enumerate(abilities):
        result += '{}'.format(ability.name)
        if i < len(abilities) - 1:
            result += ', '
    return result


def sort_abilities(abilities, with_method=None):
    if with_method:
        filtered_abilities = [ab for ab in abilities if hasattr(ab, with_method)]
    else:
        filtered_abilities = abilities.copy()
    filtered_abilities.sort(key=lambda x: x.order)
    return filtered_abilities


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

    def active_prompt(self, attacking_unit, target_unit=None, aura_unit=None):
        return None


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


class DiseasedHorde(HitModifier):

    def __init__(self):
        super().__init__('Diseased Horde', 1)

    def active_prompt(self, attacking_unit, target_unit=None, aura_unit=None):
        return '{}: Does {} unit contain more than 10 models? '.format(self.name, attacking_unit.name)


class AutoHit(Ability):
    offensive = True
    order = 3  # Go after all other hit mods

    def modify_hit_rolls(self, hit_rolls, hit_target):
        hit_rolls.fill(hit_target + 1)  # The +1 is just for my sanity
        return hit_rolls


class WoundReRoll(Ability):
    offensive = True

    def __init__(self, name, value):
        super().__init__(name)
        self.value = value

    def modify_wound_rolls(self, wound_rolls):
        failed_rolls = np.argwhere(wound_rolls <= self.value)
        reroll = np.random.randint(1, 6, size=len(failed_rolls))
        for i, failed_roll_loc in enumerate(failed_rolls):
            wound_rolls[failed_roll_loc] = reroll[i]
        return wound_rolls


class HitReRollAura(Ability):
    offensive = True
    aura = True

    def __init__(self, name, value, aura_range):
        super().__init__(name)
        self.value = value
        self.aura_range = aura_range

    def active_prompt(self, attacking_unit, target_unit=None, aura_unit=None):
        if attacking_unit == aura_unit:
            return None
        return '{}: Is {} within {}" of {}? '.format(self.name, attacking_unit.name, self.aura_range, aura_unit.name)

    def modify_hit_rolls(self, hit_rolls, hit_target):
        failed_rolls = np.argwhere(hit_rolls <= self.value)
        reroll = np.random.randint(1, 6, size=len(failed_rolls))
        for i, failed_roll_loc in enumerate(failed_rolls):
            hit_rolls[failed_roll_loc] = reroll[i]
        return hit_rolls


class Resilient(Ability):
    defensive = True

    def __init__(self, name, value):
        super().__init__(name)
        self.value = value

    def modify_damage_rolls(self, damage_rolls):
        for i, damage in enumerate(damage_rolls):
            resilient_rolls = np.random.randint(1, 7, size=damage)
            damage_reduced = (resilient_rolls >= self.value).sum()
            damage_rolls[i] = damage - damage_reduced
        return damage_rolls


class WoundReRollAura(Ability):
    offensive = True
    aura = True

    def __init__(self, name, value, aura_range):
        super().__init__(name)
        self.value = value
        self.aura_range = aura_range

    def active_prompt(self, attacking_unit, target_unit=None, aura_unit=None):
        if attacking_unit == aura_unit:
            return None
        return '{}: Is {} within {}" of {}? '.format(self.name, attacking_unit.name, self.aura_range, aura_unit.name)

    def modify_wound_rolls(self, wound_rolls):
        failed_rolls = np.argwhere(wound_rolls <= self.value)
        reroll = np.random.randint(1, 6, size=len(failed_rolls))
        for i, failed_roll_loc in enumerate(failed_rolls):
            wound_rolls[failed_roll_loc] = reroll[i]
        return wound_rolls
