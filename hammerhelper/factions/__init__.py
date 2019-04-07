from .death_guard import all_death_guard
from .space_marines import all_space_marines

all_units = [*all_death_guard, *all_space_marines]
all_units_dict = {unit.name: unit for unit in all_units}
