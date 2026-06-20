# Sekiro: Shadows Die Twice

Game Page | [Items] | [Locations]

[Items]: /tutorial/Sekiro/items/en
[Locations]: /tutorial/Sekiro/locations/en

## What do I need to do to randomize Sekiro?

See full instructions on [the setup page].

[the setup page]: /tutorial/Sekiro/setup/en

## What does randomization do to this game?

1. All item locations can be randomized, including those in the overworld, in
   shops, and dropped by enemies. Treasure Carp locations are turned off by 
   default, but can be enabled. Most locations can contain items from other 
   worlds, and any items from your world can appear in other players' worlds.

2. By default, all enemies and bosses except for Headless are randomized. This 
   can be disabled by setting "Randomize Enemies" to false.

There are also options that can make playing the game more convenient or bring 
a new experience, like removing the Headless-induced slow walk or shuffling 
skills between Esoteric Texts. Check out the Template YAML or the Option Builder
in the Archipelago Launcher for more.

## What's the goal?

There are two options available for the goal.

The "Full Game" goal is to find the "Divine Dragon's Tears" item and achieve 
one of the endings that require this item.
The "Shura" goal is achieved by joining Owl in the first invasion and defeating
the alternate final boss.

## Do I have to check every item in every area?

Sekiro has nearly 750 item locations, which is a lot of checks for a single run!
But you don't necessarily need to check all of them. Locations that you can
potentially miss, such as rewards for failable quests or areas that become 
unavailable during the game state changes, will _never_ have items required for 
any game to progress. The following types of locations are also guaranteed not 
to contain progression items by default:

* **Hidden:** Locations that are particularly difficult to find, such as in
  crawl spaces, down hidden drops, behind walls and so on. Does not include 
  large locations like Ashina Outskirts after the Central Forces invasion.

* **Upgrade:** Locations that contain non-unique upgrade materials for
  prosthetic tools in vanilla.

* **Miscellaneous:** Locations that contain generic stackable items such as
  sugars, coin pouches, mibu balloons, resistance buffs and so on.

You can customize which locations are guaranteed not to contain progression
items by setting the `exclude_locations` field in your YAML to the [location
groups] you want to omit. For example, this is the default setting but without
"Hidden" so that hidden locations can contain progression items:

[location groups]: /tutorial/Sekiro/locations/en#location-groups

```yaml
Shadows Die Twice:
  exclude_locations:
    - Upgrade
    - Miscellaneous
```

This allows _all_ non-missable locations to have progression items, if you're in
for the long haul:

```yaml
Shadows Die Twice:
  exclude_locations: []
```

## What if I don't want to do the whole game?

If you want a shorter Sekiro randomizer experience, you can choose the Shura 
ending. This will allow you to end the game after the first invasion and 
removes several late-game regions entirely. Combining this with the default 
exclusions will give you a pretty quick game.

## Where can I learn more about Sekiro locations?

Location names have to pack a lot of information into very little space. To
better understand them, check out the [location guide], which explains all the
names used in locations and provides more detailed descriptions for each
individual location.

[location guide]: /tutorial/Sekiro/locations/en

## Where can I learn more about Sekiro items?

Check out the [item guide], which explains the named groups available for items.

[item guide]: /tutorial/Sekiro/items/en
