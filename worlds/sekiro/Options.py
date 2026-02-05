from dataclasses import dataclass
import json
from typing import Any, Dict

from Options import Choice, DeathLink, DefaultOnToggle, ExcludeLocations, OptionDict, \
    OptionGroup, PerGameCommonOptions, Removed, Toggle

## Game Options


class QuickHirata(Choice):
    """Force the Young Lord's Bell Charm to be early in your local world or the multiworld"""
    display_name = "Quick Hirata"
    option_off = 0
    option_early_global = 1
    option_early_local = 2
    default = option_off


class VeryEarlyHirata(Choice):
    """Make it possible to need to progress into Hirata Estate before Ashina Outskirts (no softlock)"""
    display_name = "Allow Very Early Hirata"
    option_off = 0
    option_early_global = 1
    option_early_local = 2
    default = option_off

## Skills
class RandomizeSkillsItemOption(Toggle):
    """Randomize the Skills as Item pickups """
    display_name = "Randomize Skills"

### Enemies

class RandomizeEnemiesOption(DefaultOnToggle):
    """Randomize enemy and boss placements."""
    display_name = "Randomize Enemies"


class RandomizeHeadlessOption(Toggle):
    """Include headless in the randomizer pool for minibosses (non-underwater)

    This is ignored unless enemies are randomized.
    """
    display_name = "Randomize Headless"


class SimilarBossPhases(DefaultOnToggle):
    """Prevent fights to be something like Sword Saint Isshin + Demon of Hatred.

     This setting will try to keep a similar number of phases compared to the replaced vanilla bosses.

     This is ignored unless enemies are randomized.
     """
    display_name = "Similar Number of Boss Phases"


class BalancedEndgameBossPhases(DefaultOnToggle):
    """Prevent early bosses to be seriously unfun by considering late game boss phases as longer than earlier ones.

    This is ignored unless enemies are randomized.
    """
    display_name = "Smoothed Boss Phases"


class SimpleEarlyMinibosses(DefaultOnToggle):
    """Prevent early minibosses from being unfun without scaling.

    This is ignored unless enemies are randomized.
    """
    display_name = "Simple Early Minibosses"


class ScaleEnemiesOption(DefaultOnToggle):
    """Scale randomized enemy stats to match the areas in which they appear.

    Disabling this will tend to make the early game much more difficult and the late game much
    easier.

    This is ignored unless enemies are randomized.
    """
    display_name = "Scale Enemies"


class RandomEnemyPresetOption(OptionDict):
    """The YAML preset for the static enemy randomizer.

    See the static randomizer documentation in `randomizer\\presets\\README.txt` for details.
    Include this as nested YAML. For example:

    .. code-block:: YAML

      random_enemy_preset:
        RemoveSource: Ancient Wyvern; Darkeater Midir
        DontRandomize: Iudex Gundyr
    """
    display_name = "Random Enemy Preset"
    supports_weighting = False
    default = {}

    valid_keys = ["Description", "RecommendFullRandomization", "RecommendNoEnemyProgression",
                  "OopsAll", "Boss", "Miniboss", "Basic", "BuffBasicEnemiesAsBosses",
                  "DontRandomize", "RemoveSource", "Enemies"]

    @classmethod
    def get_option_name(cls, value: Dict[str, Any]) -> str:
        return json.dumps(value)


## Item & Location

class Carpsanity(Toggle):
    """Add Treasure Carp drops into the item pool"""
    display_name = "Carpsanity"


class SekiroExcludeLocations(ExcludeLocations):
    """Prevent these locations from having an important item."""
    default = frozenset({"Hidden", "Upgrade", "Currency", "Miscellaneous"})


class ExcludedLocationBehaviorOption(Choice):
    """How to choose items for excluded locations in DS3.

    - **Allow Useful:** Excluded locations can't have progression items, but they can have useful
      items.
    - **Forbid Useful:** Neither progression items nor useful items can be placed in excluded
      locations.
    - **Do Not Randomize:** Excluded locations always contain the same item as in vanilla Dark Souls
      III.

    A "progression item" is anything that's required to unlock another location in some game. A
    "useful item" is something each game defines individually, usually items that are quite
    desirable but not strictly necessary.
    """
    display_name = "Excluded Locations Behavior"
    option_allow_useful = 1
    option_forbid_useful = 2
    option_do_not_randomize = 3
    default = 2


class MissableLocationBehaviorOption(Choice):
    """Which items can be placed in locations that can be permanently missed.

    - **Allow Useful:** Missable locations can't have progression items, but they can have useful
      items.
    - **Forbid Useful:** Neither progression items nor useful items can be placed in missable
      locations.
    - **Do Not Randomize:** Missable locations always contain the same item as in vanilla Dark Souls
      III.

    A "progression item" is anything that's required to unlock another location in some game. A
    "useful item" is something each game defines individually, usually items that are quite
    desirable but not strictly necessary.
    """
    display_name = "Missable Locations Behavior"
    option_allow_useful = 1
    option_forbid_useful = 2
    option_do_not_randomize = 3
    default = 2


@dataclass
class SekiroOptions(PerGameCommonOptions):
    # Game Options
    quick_hirata: QuickHirata
    very_early_hirata: VeryEarlyHirata
    death_link: DeathLink

    # Skills
    randomize_skills: RandomizeSkillsItemOption

    # Enemies
    randomize_enemies: RandomizeEnemiesOption
    randomize_headless: RandomizeHeadlessOption
    similar_boss_phases: SimilarBossPhases
    balanced_endgame_boss_phases: BalancedEndgameBossPhases
    simple_early_minibosses: SimpleEarlyMinibosses
    scale_enemies: ScaleEnemiesOption
    random_enemy_preset: RandomEnemyPresetOption

    # Item & Location
    carpsanity: Carpsanity
    exclude_locations: SekiroExcludeLocations
    excluded_location_behavior: ExcludedLocationBehaviorOption
    missable_location_behavior: MissableLocationBehaviorOption


option_groups = [
    OptionGroup("Skills", [
        RandomizeSkillsItemOption,
    ]),
    OptionGroup("Enemies", [
        RandomizeEnemiesOption,
        RandomizeHeadlessOption,
        SimilarBossPhases,
        BalancedEndgameBossPhases,
        SimpleEarlyMinibosses,
        ScaleEnemiesOption,
        RandomEnemyPresetOption,
    ]),
    OptionGroup("Item & Location Options", [
        Carpsanity,
        SekiroExcludeLocations,
        ExcludedLocationBehaviorOption,
        MissableLocationBehaviorOption,
    ])
]
