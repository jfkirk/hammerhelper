from tabulate import tabulate

from units import all_units_dict


def print_army_ids(army):
    headers = ['Unit #', 'Name']
    units = [
        [unit_number + 1, army[unit_number].name]
        for unit_number in range(len(army))
    ]
    print(tabulate(units, headers, tablefmt='psql'))

if __name__ == '__main__':

    friendly_army = [all_units_dict['Intercessor'], all_units_dict['Intercessor']]
    enemy_army = [all_units_dict['Intercessor'], all_units_dict['Intercessor']]

    print_army_ids(friendly_army)
