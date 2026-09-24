# Sekiro: Shadows Die Twice Enemy Randomization

[Game Page] | [Setup] | [Items] | [Locations] | Enemy Randomization

[Game Page]: /worlds/sekiro/docs/en_Sekiro%20Shadows%20Die%20Twice.md
[Setup]: /worlds/sekiro/docs/setup_en.md
[Items]: /worlds/sekiro/docs/items_en.md
[Locations]: /worlds/sekiro/docs/locations_en.md

If `enemy_randomizer` in your Sekiro player config YAML is enabled, bosses, minibosses and basic enemies will
be shuffled with themselves respectively if they are enabled.

`randomize_headless` additionally adds Headless enemies into the pool of minibosses.

To further customize enemy randomization beyond that, there is a section called `random_enemy_preset`.

This tutorial will show all the ways how to configure that preset.

## Table of Contents
- [The Basics](#the-basics)
- [Individual Assignments](#individual-assignments)
- [Pools](#pools)
  * [Pool Groups](#pool-groups)
    + [RandomByType](#randombytype)
  * [Weights](#weights)
- [Settings](#settings)
  * [Boss](#boss)
  * [Miniboss](#miniboss)
  * [Basic](#basic)
    + [BuffBasicEnemiesAsBosses](#buffbasicenemiesasbosses)
  * [Enemies](#enemies)
  * [DontRandomize](#dontrandomize)
  * [RemoveSource](#removesource)
  * [OopsAll](#oopsall)
- [Enemy Categories](#enemy-categories)

## The Basics

There are two main ways to assign an enemy to be randomized: [individual enemy assignments](#individual-assignments)
to target a singular enemy placement and setting up [Pools](#pools) to target a category of enemies.

Custom pools are recommended unless you specifically want to single out one enemy placement.

All bosses also have their own category, so individual assignment is not necessary in those cases.

Be aware of correct indentation of your YAML file. Every example in this document will need to be nested under the
`random_enemy_preset:` section.

Disable the preset by leaving just empty brackets `{}`. Like usual with YAML, you can add comments by using `#`.

For further examples, check out the "presets" folder of the standalone randomizer.

## Individual Assignments

Individual enemy assignment allows you to target individual enemies, rather than a category as under pools.

This overrides pools and any other configuration and will usually ignore progression. This can force a boss with many
phases early on despite `similar_boss_phases` being enabled.

You use it in the [`Enemies`](#enemies) section by selecting a specific enemy using its unique
ID, or its specific name followed by its ID.

See the '/randomizer/preset/Template.txt' file of the static randomizer for all available IDs.

There are also some special target names available for individual assignments:

- `any`: This is the default and allows any enemy in the pool to appear there.

- `norandom`: Assigns an enemy to itself. This has the same effect as adding the enemy name to [`DontRandomize`](#dontrandomize).

## Pools

A pool is a collection of enemies. A pool can both be a randomization target and an eligible group of random enemies to
be drawn from for randomization. See [Enemy Categories](#enemy-categories) for all available pools.

Pool assignment generally respects progression, like the phase scaling of `similar_boss_phases`.

By default, using a boss as another boss or a miniboss as another miniboss takes the source enemy out of the default
pool for that category, so each enemy will still be used once if possible. However, the enemy can still appear more
than once if used in a custom pool.

### Pool Groups

Pools can be joined into a pool group by joining several names, separated by a semicolon.

```yaml
# All basic enemies are animals now
Basic:
- Weight: 100
  Pool: Valley Monkey; Cricket
```

#### RandomByType

By default, selection will be random across all eligible enemies. In our example above it would select from:

- Valley Monkey
- Elder Valley Monkey
- Terror Valley Monkey

and

- Aggressive Cricket
- Passive Cricket

However, this would make it more likely to select a monkey instead of a cricket (3 out of 5), just because
there are fewer entries in the latter category.

You can specify `RandomByType: true` to select randomly from the list itself (Valley Monkey, Cricket)
and make our previous example a true 50/50 split.

```yaml
# All basic enemies are animals now
Basic:
- Weight: 100
  Pool: Valley Monkey; Cricket
  RandomByType: true # To make it truly 50/50 between the categories
```

### Weights

Weights can be used to select multiple different outcomes within a pool, weighted to give different probabilities each.

Weights don't necessarily have to add up to 100, but doing it that way makes estimating probabilities very intuitive.

```yaml
Boss:
- Weight: 79 # 79% of bosses will still be bosses
  Pool: default
- Weight: 20 # Replace 20% of all bosses with minibosses
  Pool: Miniboss
- Weight: 1 # Replace 1% of all bosses with regular enemies. It's always funny
  Pool: Basic
```

Be aware that weights will not work in the [`Enemies`](#enemies) section.

## Settings

### Boss

This setting indicates which enemies can be used as replacements for bosses.
By default, this is the pool of all 22 bosses.

```yaml
Boss:
- Weight: 80
  Pool: default
- Weight: 20 # Replace 20% of all bosses with minibosses
  Pool: Miniboss
```

### Miniboss

This setting indicates which enemies can be used as replacements for minibosses.
By default, this is the pool of all 35 minibosses (including duplicates).

```yaml
Miniboss:
- Weight: 80
  Pool: default
- Weight: 20 # Replace 20% of all minibosses with bosses
  Pool: Boss
```

### Basic

This setting indicates which enemies can be used as replacements for all other enemies, so non-bosses and non-minibosses.
By default, this is the pool of all ~1140 basic enemies (including duplicates).

```yaml
Basic:
- Weight: 94
  Pool: default
- Weight: 5 # Replace 5% of all basic enemies with minibosses
  Pool: Miniboss
- Weight: 1 # Replace 1% of all basic enemies with bosses
  Pool: Boss
```

#### BuffBasicEnemiesAsBosses

If enabled, this causes basic enemies to become a lot stronger when randomized into the slot of a boss.

```yaml
Boss:
- Weight: 100 # All bosses are just basic enemies...
  Pool: Basic

BuffBasicEnemiesAsBosses: true # ...but they are strong
```

### Enemies

Under the `Enemies:` setting you can add more nuanced replacements of random enemies.
There are two ways you can adjust enemies:
- Assign to a group of enemies using their category pool (see [Enemy Categories](#enemy-categories))
- Assign to one specifc enemy by using its number (see [Individual Assignments](#individual-assignments))

```yaml
Enemies:
  # Replace only the tutorial enemy around the corner with the final boss
  Tutorial Ashina Soldier 1120204: Sword Saint Isshin
  
  # Replace all regular soldiers with dive bomb ninjas
  Ashina Soldier: Kite Nightjar Ninja
  
  # Valley clan remains valley clan, but variants (i.e. weapons) are still shuffled within the category
  Sunken Valley Clan: Sunken Valley Clan
```

### DontRandomize

A semicolon-separated list of enemies or enemy types to not randomize (assign to themselves).
It is taken out of its default pool and also custom pools in this case, but it can still be assigned to
[individual enemies](#individual-assignments).

```yaml
DontRandomize: Gyoubu Oniwa # Gyoubu will be at his vanilla location

Boss:
- Weight: 100
  Pool: default # Boss slots other than Gyoubu will never become him
```

### RemoveSource

A semicolon-separated list of enemies or enemy types to remove from all pools.
It can still be assigned to individual enemies.
This is overridden by [`DontRandomize`](#dontrandomize) directives.

```yaml
# Remove the most annoying or difficult enemies from all pools
RemoveSource: Divine Dragon; Demon of Hatred; Spear Adept
```

### OopsAll

Assigning an enemy or a pool to `OopsAll` sets all pools to that specific enemy or category of enemy. This can still be
overridden using [individual enemy assignments](#individual-assignments), but otherwise every enemy is replaced by
this setting.

```yaml
# Monkey business
OopsAll: Valley Monkey
```

---

## Enemy Categories

The following enemy category pools are available:

- Any
- Bosses
- Minibosses
- Bosses and Minibosses
- Basic
- Armored Warrior
- Ashina Soldier
  - Katana Ashina Soldier
  - Defensive Ashina Soldier
  - Spear Ashina Soldier
  - Rifle Ashina Sodlier
- Assassin (Interior Ministry)
- Assassin (Senpou)
- Bandit
- Blazing Bull
- Centipede
- Centipede Boss
  - Long-arm Centipede Giraffe
  - Long-arm Centipede Sen'un
- Chained Ogre
- Corrupted Monk
- Cricket
  - Aggressive Cricket
  - Passive Cricket
- Demon of Hatred
- Divine Dragon
- Divine Dragon and Old Dragons
  - Divine Dragon
  - Old Dragon
- Emma
- Fencer
  - Basic Fencer
  - Ashina Elite Jinsuke Saze
  - Ashina Elite Ujinari Mizuo
- Folding Screen Monkey
  - Folding Screen Monkey (Seeing)
  - Folding Screen Monkey (Hearing)
  - Folding Screen Monkey (Speaking)
  - Folding Screen Monkey (Invisible)
- Gamefowl
- Gecko
- Genichiro Ashina
- Genichiro Ashina (Tutorial)
- Genichiro, Way of Tomoe (Lightning)
- Genichiro, Way of Tomoe (Mortal Blade)
- Great Shinobi Owl
- Guardian Ape
- Gyoubu Oniwa
- Headless
- Headless Ape
- Hound
- Infested Seeker
- Infested Seeker (Parasite)
- Isshin Ashina
- Lady Butterfly 1
- Lady Butterfly 2
- Lone Shadow
  - Basic Lone Shadow
  - Lone Shadow Longswordsman
  - Lone Shadow Masanaga the Spear-Bearer (Ashina Castle)
  - Lone Shadow Masanaga the Spear-Bearer (Hirata)
  - Lone Shadow Vilehand
- Mibu Villager
  - Grabbing Mibu Villager
- Nightjar Ninja
  - Exploding Nightjar Ninja
  - Kite Nightjar Ninja
- Okami Warrior
  - Katana Okami Warrior
  - Naginata Okami Warrior
  - Bow Okami Warrior
  - Ball Okami Warrior
  - Lightning Okami Warrior
  - Okami Leader Shizu
- Old Dragon
- Old Maid
- Old Maid (Sunken Valley)
- Owl (Father)
- O'Rin
- Palace Hound
- Palace Noble
  - Blue Palace Noble
  - Red Palace Noble
  - Mist Noble
- Red Guard
  - Dual Katana Red Guard
  - Firebomb Red Guard
  - Flamethrower Red Guard
- Rock Diver
- Sakura Bull of the Palace
- Samurai General
  - Basic Samurai General
  - Leader Shigenori Yamauchi
  - General Naomori Kawarada
  - General Tenzen Yamauchi
  - General Kuranosuke Matsomoto
- Seeker
- Sentry
- Seven Ashina Spears
  - Seven Ashina Spears 1
  - Seven Ashina Spears 2
- Shichimen Warrior
- Shinobi Hunter
- Shura Samurai
  - Juzou the Drunkard
  - Juzou the Drunkard 2
  - Shigekichi of the Red Guard
  - Tokujiro the Glutton
- Snake Eyes
  - Snake Eyes Shirafuji
  - Snake Eyes Shirahagi
- Spear Adept
- Sunken Valley Clan
  - Rifle Sunken Valley Clan
  - Scattershot Sunken Valley Clan
  - Cannon Sunken Valley Clan
  - Sniper Sunken Valley Clan
- Sword Saint Isshin
- Taro Troop
- Taro Troop (Mibu)
- Test Subject
- True Monk
- Tutorial Ashina Soldier
- Valley Monkey
  - Elder Valley Monkey
  - Terror Valley Monkey
