#!/usr/bin/env python

from distutils.util import strtobool
from tabulate import tabulate

from factions.abilities import string_from_ability_list
from sim import simulate
from factions import all_units_dict


QUIT_COMMANDS = ['q', 'Q']

FRIENDLY_ARMY = [all_units_dict['Captain in Gravis Armor'],
                 all_units_dict['Primaris Lieutenant'],
                 all_units_dict['Primaris Ancient'],
                 all_units_dict['Primaris Apothecary'],
                 all_units_dict['Redemptor Dreadnaught'],
                 all_units_dict['Inceptor'],
                 all_units_dict['Aggressor'],
                 all_units_dict['Hellblaster'],
                 all_units_dict['Intercessor'],
                 all_units_dict['Blightlord Terminator'],
                 all_units_dict['Plague Marine'],
                 all_units_dict['Poxwalker']]
ENEMY_ARMY = FRIENDLY_ARMY


def print_army(army):
    headers = ['Unit #', 'Name', 'M', 'WS', 'BS', 'S', 'T', 'W', 'A', 'Ld', 'Sv', 'Abilities']
    units = [
        [unit_number + 1,
         army[unit_number].name,
         '{}"'.format(army[unit_number].m),
         '{}+'.format(army[unit_number].ws),
         '{}+'.format(army[unit_number].bs),
         army[unit_number].s,
         army[unit_number].t,
         army[unit_number].w,
         army[unit_number].a,
         army[unit_number].ld,
         '{}+'.format(army[unit_number].sv),
         string_from_ability_list(army[unit_number].abilities),]
        for unit_number in range(len(army))
    ]
    print(tabulate(units, headers, tablefmt='psql'))


def print_weapons(weapons, unit):

    def unit_value_mask(weapon_value, effective_value):
        if 'U' in str(weapon_value):
            return '{}({})'.format(effective_value, weapon_value)
        return weapon_value

    headers = ['Weapon #', 'Name', 'Range', 'Type', 'A', 'S', 'AP', 'D', 'Abilities']
    weapons_rows = [
        [weapon_number + 1,
         weapons[weapon_number].name,
         '{}"'.format(weapons[weapon_number].weapon_range),
         weapons[weapon_number].weapon_type.name,
         unit_value_mask(weapons[weapon_number].a, weapons[weapon_number].effective_attacks(unit)),
         unit_value_mask(weapons[weapon_number].s, weapons[weapon_number].effective_strength(unit)),
         weapons[weapon_number].ap,
         weapons[weapon_number].d,
         string_from_ability_list(weapons[weapon_number].abilities),]
        for weapon_number in range(len(weapons))
    ]
    print(tabulate(weapons_rows, headers, tablefmt='psql'))


def print_sim_results(sim_results):
    headers = ['Target Name', 'Attacks', 'H', 'Hits', 'W', 'Wounds', 'Sv', 'Damage', 'Kills']
    print(tabulate(sim_results, headers, tablefmt='psql'))


def boolean_prompt(text):
    result = None
    while result is None:
        try:
            response = input(text)
            result = strtobool(response)
        except ValueError:
            print('Invalid response "{}", try "T" or "F"'.format(response))
    return result


def number_prompt(text, max_val=None):
    while True:
        response = input(text)
        if response in QUIT_COMMANDS:
            return None
        try:
            selection = int(response)
        except ValueError:
            if max_val:
                print('Invalid selection, must be between 1 and {} or `q` to restart'.format(max_val))
            else:
                print('Invalid selection, try again or `q` to restart')
            continue
        if max_val and (selection > max_val):
            print('Invalid selection, must be between 1 and {} or `q` to restart'.format(max_val))
            continue
        return selection


def maybe_prompt_for_ability(ability, attacking_unit, target_unit=None, aura_unit=None):
    prompt_string = ability.active_prompt(attacking_unit, target_unit, aura_unit)
    if prompt_string:
        return boolean_prompt(prompt_string)
    else:
        return True


def input_attack(army):
    print_army(army)
    attacking_unit_id = number_prompt('Select an attacking unit #: ', len(army))
    if attacking_unit_id is None:
        return None, None, None

    attacking_unit = FRIENDLY_ARMY[attacking_unit_id-1]  # Map to Unit objects
    print_weapons(weapons=attacking_unit.weapons,
                  unit=attacking_unit)
    attacking_weapon_id = number_prompt('Select a weapon #: ', len(attacking_unit.weapons))
    if attacking_weapon_id is None:
        return None, None, None

    attacking_weapon = attacking_unit.weapons[attacking_weapon_id-1]

    print('Selected:')
    print_army([attacking_unit])
    print_weapons([attacking_weapon], attacking_unit)

    if 'D' in str(attacking_weapon.a):
        print('Note: For weapons with a dice value for `A`, '
              'the number of shots is the number of times the unit fires the weapon.')
    n_shots = number_prompt('How many shots: ')

    return attacking_unit, attacking_weapon, n_shots


def map_abilities(attacking_unit, weapon, target_units, friendly_army, enemy_army):
    result = {}

    # These abilities apply to all targets
    offensive_abilities = []
    offensive_abilities.extend([ab for ab in attacking_unit.offensive_abilities
                                if maybe_prompt_for_ability(ab, attacking_unit)])
    offensive_abilities.extend([ab for ab in weapon.offensive_abilities
                                if maybe_prompt_for_ability(ab, attacking_unit)])
    for friendly_unit in friendly_army:
        offensive_abilities.extend([ab for ab in friendly_unit.offensive_auras
                                    if maybe_prompt_for_ability(ab, attacking_unit, aura_unit=friendly_unit)])

    for target_unit in target_units:

        # These abilities apply to specific targets
        abilities_per_target = offensive_abilities.copy()
        abilities_per_target.extend([ab for ab in attacking_unit.offensive_targeted_abilities
                                     if maybe_prompt_for_ability(ab, attacking_unit, target_unit)])
        abilities_per_target.extend([ab for ab in weapon.offensive_targeted_abilities
                                     if maybe_prompt_for_ability(ab, attacking_unit, target_unit)])
        abilities_per_target.extend([ab for ab in target_unit.defensive_abilities
                                     if maybe_prompt_for_ability(ab, attacking_unit, target_unit)])

        for friendly_unit in friendly_army:
            abilities_per_target.extend([ab for ab in friendly_unit.offensive_targeted_auras
                                         if maybe_prompt_for_ability(ab, attacking_unit, target_unit, friendly_unit)])
        for enemy_unit in enemy_army:
            abilities_per_target.extend([ab for ab in enemy_unit.defensive_auras
                                         if maybe_prompt_for_ability(ab, attacking_unit, target_unit, enemy_unit)])

        result[target_unit.name] = abilities_per_target

    return result


def main_loop():

    while True:
        attacking_unit, weapon, n_shots = input_attack(FRIENDLY_ARMY)
        if n_shots is None:
            continue

        abilities_by_target = map_abilities(attacking_unit, weapon, ENEMY_ARMY, FRIENDLY_ARMY, ENEMY_ARMY)

        all_sim_results = simulate(attacking_unit, weapon, n_shots, ENEMY_ARMY, abilities_by_target)
        print_sim_results(all_sim_results)
        input('Press any key to continue...')


if __name__ == '__main__':

    main_loop()
