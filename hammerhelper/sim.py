import numpy as np
import progressbar

from units import WeaponType


N_SIMS = 10000


def roll_dice(d, size):
    return np.random.randint(1, d + 1, size=size)


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


def calculate_save_target_value(weapon, target_unit, active_abilities):
    target = target_unit.sv - weapon.ap

    # "A roll of 1 always fails, irrespective of any modifiers that may apply."
    if target < 2:
        target = 2

    for ability in active_abilities:
        target = ability.modify_save_target(target)

    return target


def simulate(attacking_unit, weapon, n_shots, target_units, friendly_army, enemy_army):
    all_sim_results = []

    offensive_abilities = []
    offensive_abilities.extend([ab for ab in attacking_unit.offensive_abilities
                                if ab.is_active_prompt(attacking_unit)])
    offensive_abilities.extend([ab for ab in weapon.offensive_abilities
                                if ab.is_active_prompt(attacking_unit)])
    for friendly_unit in friendly_army:
        offensive_abilities.extend([ab for ab in friendly_unit.offensive_auras
                                    if ab.is_active_prompt(attacking_unit, aura_unit=friendly_unit)])

    print('Simulating...')
    bar = progressbar.ProgressBar(
        maxval=len(target_units),
        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()]
    )
    bar.start()

    for i, target_unit in enumerate(target_units):
        sim_result = [target_unit.name]
        sim_result.extend(simulate_unit(attacking_unit, weapon, n_shots, target_unit, offensive_abilities,
                                        friendly_army, enemy_army))
        all_sim_results.append(sim_result)
        bar.update(i + 1)

    bar.finish()

    return all_sim_results


def simulate_unit(attacking_unit, weapon, n_shots, target_unit, offensive_abilities, friendly_army, enemy_army):

    all_abilities = offensive_abilities.copy()
    all_abilities.extend([ab for ab in attacking_unit.offensive_targeted_abilities
                          if ab.is_active_prompt(attacking_unit, target_unit)])
    all_abilities.extend([ab for ab in weapon.offensive_targeted_abilities
                          if ab.is_active_prompt(attacking_unit, target_unit)])
    all_abilities.extend([ab for ab in target_unit.defensive_abilities
                          if ab.is_active_prompt(attacking_unit, target_unit)])

    for friendly_unit in friendly_army:
        all_abilities.extend([ab for ab in friendly_unit.offensive_targeted_auras
                              if ab.is_active_prompt(attacking_unit, target_unit, friendly_unit)])
    for enemy_unit in enemy_army:
        all_abilities.extend([ab for ab in enemy_unit.defensive_auras
                              if ab.is_active_prompt(attacking_unit, target_unit, enemy_unit)])

    # Sort abilities on their "order" value
    all_abilities.sort(key=lambda x: x.order)

    hit_target_value = attacking_unit.ws if weapon.weapon_type == WeaponType.MELEE else attacking_unit.bs
    t, s, wound_target_value = calculate_wound_target_value(attacking_unit, weapon, target_unit)
    save_target_value = calculate_save_target_value(weapon, target_unit, all_abilities)

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
        for ability in all_abilities:
            hit_rolls = ability.modify_hit_rolls(hit_rolls, hit_target_value)
        n_hits = (hit_rolls >= hit_target_value).sum()

        # Roll the wound dice
        wound_rolls = roll_dice(6, size=n_hits)
        for ability in all_abilities:
            wound_rolls = ability.modify_wound_rolls(wound_rolls)
        n_wounds = (wound_rolls >= wound_target_value).sum()

        # Roll the save dice
        save_rolls = roll_dice(6, size=n_wounds)
        n_unsaved = n_wounds - (save_rolls >= save_target_value).sum()

        # Roll damage
        damage_rolls = maybe_roll_from_dice_string(weapon.d, size=n_unsaved)
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
