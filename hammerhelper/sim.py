import numpy as np
import progressbar

from factions.abilities import sort_abilities
from factions.units import WeaponType
from util import roll_dice


N_SIMS = 10000


def roll_from_dice_string(dice_string, size):
    if dice_string == 'D3':
        return roll_dice(3, size=size)
    elif dice_string == 'D6':
        return roll_dice(6, size=size)
    elif dice_string == '2D6':
        return roll_dice(6, size=size) + roll_dice(6, size=size)
    else:
        raise Exception('Invalid dice string')


def maybe_roll_from_dice_string(input_val, size):
    try:
        return roll_from_dice_string(input_val, size)
    except:
        return np.full(size, input_val)


def calculate_wound_target_value(attacking_unit, weapon, target_unit):
    t = target_unit.t
    s = weapon.effective_strength(attacking_unit)

    if s >= (2 * t):
        return t, s, 2
    if s > t:
        return t, s, 3
    if s == t:
        return t, s, 4
    if s > (.5 * t):  # TODO rounding?
        return t, s, 5
    return t, s, 6


def calculate_save_target_value(weapon, target_unit, save_target_abilities):
    target = target_unit.sv - weapon.ap

    # "A roll of 1 always fails, irrespective of any modifiers that may apply."
    if target < 2:
        target = 2

    for ability in save_target_abilities:
        target = ability.modify_save_target(target)

    return target


def simulate(attacking_unit, weapon, n_shots, target_units, abilities_by_target):
    all_sim_results = []

    print('Simulating...')
    bar = progressbar.ProgressBar(
        maxval=len(target_units),
        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()]
    )
    bar.start()

    for i, target_unit in enumerate(target_units):
        active_abilities = abilities_by_target[target_unit.name]
        sim_result = [target_unit.name]
        sim_result.extend(simulate_unit(attacking_unit, weapon, n_shots, target_unit, active_abilities))
        all_sim_results.append(sim_result)
        bar.update(i + 1)

    bar.finish()

    return all_sim_results


def simulate_unit(attacking_unit, weapon, n_shots, target_unit, active_abilities):

    # Sort abilities on their "order" value
    save_target_abilities = sort_abilities(active_abilities, with_method='modify_save_target')
    hit_mod_abilities = sort_abilities(active_abilities, with_method='modify_hit_rolls')
    wound_mod_abilities = sort_abilities(active_abilities, with_method='modify_wound_rolls')
    damage_mod_abilities = sort_abilities(active_abilities, with_method='modify_damage_rolls')

    hit_target_value = attacking_unit.ws if weapon.weapon_type == WeaponType.MELEE else attacking_unit.bs
    t, s, wound_target_value = calculate_wound_target_value(attacking_unit, weapon, target_unit)
    save_target_value = calculate_save_target_value(weapon, target_unit, save_target_abilities)

    sims_attacks_hits_wounds_damages_kills = []

    for sim in range(N_SIMS):

        # If applicable, roll for n_attacks
        weapon_effective_attacks = weapon.effective_attacks(attacking_unit)
        if 'D' in str(weapon_effective_attacks):  # TODO don't do this string conversion in the tight loop
            n_attacks = sum(roll_from_dice_string(weapon_effective_attacks, size=n_shots))
        else:
            n_attacks = n_shots

        # Roll the attack dice
        hit_rolls = roll_dice(6, size=n_attacks)
        for ability in hit_mod_abilities:
            hit_rolls = ability.modify_hit_rolls(hit_rolls, hit_target_value)
        n_hits = (hit_rolls >= hit_target_value).sum()

        # Roll the wound dice
        wound_rolls = roll_dice(6, size=n_hits)
        for ability in wound_mod_abilities:
            wound_rolls = ability.modify_wound_rolls(wound_rolls, wound_target_value)
        n_wounds = (wound_rolls >= wound_target_value).sum()

        # Roll the save dice
        save_rolls = roll_dice(6, size=n_wounds)
        n_unsaved = n_wounds - (save_rolls >= save_target_value).sum()

        # Roll damage
        damage_rolls = maybe_roll_from_dice_string(weapon.d, size=n_unsaved)
        for ability in damage_mod_abilities:
            damage_rolls = ability.modify_damage_rolls(damage_rolls)
        total_damage = sum(damage_rolls)

        # Allocate damage and count kills
        n_kills, allocated_damage = 0, 0
        for dmg in damage_rolls:
            allocated_damage += dmg
            if allocated_damage >= target_unit.w:
                n_kills += 1
                allocated_damage = 0

        sims_attacks_hits_wounds_damages_kills.append((n_attacks, n_hits, n_wounds, total_damage, n_kills))

    # Unzip results and calculate percentiles
    all_attacks, all_hits, all_wounds, all_damages, all_kills = \
        (list(res) for res in zip(*sims_attacks_hits_wounds_damages_kills))
    index_5th = int(.05 * N_SIMS)
    index_25th = int(.25 * N_SIMS)
    index_median = int(.5 * N_SIMS)
    index_75th = int(.75 * N_SIMS)
    index_95th = int(.95 * N_SIMS)

    all_attacks.sort()
    attacks_result = (all_attacks[index_5th], all_attacks[index_25th], all_attacks[index_median],
                      all_attacks[index_75th], all_attacks[index_95th],)

    all_hits.sort()
    hits_result = (all_hits[index_5th], all_hits[index_25th], all_hits[index_median],
                   all_hits[index_75th], all_hits[index_95th],)

    all_wounds.sort()
    wounds_result = (all_wounds[index_5th], all_wounds[index_25th], all_wounds[index_median],
                     all_wounds[index_75th], all_wounds[index_95th],)

    all_damages.sort()
    damages_result = (all_damages[index_5th], all_damages[index_25th], all_damages[index_median],
                      all_damages[index_75th], all_damages[index_95th],)

    all_kills.sort()
    kills_result = (all_kills[index_5th], all_kills[index_25th], all_kills[index_median],
                    all_kills[index_75th], all_kills[index_95th],)

    return [attacks_result, "{}+".format(hit_target_value), hits_result, "{}+".format(wound_target_value),
            wounds_result, "{}+".format(save_target_value), damages_result, kills_result]
