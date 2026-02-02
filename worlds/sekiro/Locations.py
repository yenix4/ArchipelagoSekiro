from typing import cast, ClassVar, Optional, Dict, List, Set
from dataclasses import dataclass

from BaseClasses import ItemClassification, Location, Region
from .Items import SekiroItemCategory, item_dictionary
from .Options import SekiroOptions

# Regions in approximate order of reward, mostly measured by how high-quality the upgrade items are
# in each region.
region_order = [
    "Ashina Reservoir - Tutorial",
    "Dilapidated Temple",
    "Ashina Outskirts",
    "Hirata Estate - Young Lord's Bell Charm",
    "Ashina Castle",
    "Ashina Reservoir - Revisit"
    "Abandoned Dungeon",
    "Senpou Temple, Mt. Kongo",
    "Sunken Valley",
    "Sunken Valley Passage",
    "Hidden Forest",
    "Poison Pool",
    "Mibu Village",
    "Ashina Castle - Interior Ministry",
    "Hirata Estate - Father's Bell Charm",
    "Fountainhead Palace",
    "Ashina Castle - Central Forces",
    "Ashina Outskirts - Burning",
    "Ashina Reservoir - Endgame",
]


@dataclass
class SekiroLocationData:
    __location_id: ClassVar[int] = 100000
    """The next location ID to use when creating location data."""

    name: str
    """The name of this location according to Archipelago.

    This needs to be unique within this world."""

    default_item_name: Optional[str]
    """The name of the item that appears by default in this location.

    If this is None, that indicates that this location is an "event" that's
    automatically considered accessed as soon as it's available. Events are used
    to indicate major game transitions that aren't otherwise gated by items so
    that progression balancing and item smoothing is more accurate for DS3.
    """

    ap_code: Optional[int] = None
    """Archipelago's internal ID for this location (also known as its "address")."""

    region_value: int = 0
    """The relative value of items in this location's region.

    This is used to sort locations when placing items like the base game.
    """

    static: Optional[str] = None
    """The key in the static randomizer's Slots table that corresponds to this location.

    By default, the static randomizer chooses its location based on the region and the item name.
    If the item name is unique across the whole game, it can also look it up based on that alone. If
    there are multiple instances of the same item type in the same region, it will assume its order
    (in annotations.txt) matches Archipelago's order.

    In cases where this heuristic doesn't work, such as when Archipelago's region categorization or
    item name disagrees with the static randomizer's, this field is used to provide an explicit
    association instead.
    """

    missable: bool = False
    """Whether this item is possible to permanently lose access to.

    This is also used for items that are *technically* possible to get at any time, but are
    prohibitively difficult without blocking off other checks (items dropped by NPCs on death
    generally fall into this category).

    Missable locations are always marked as excluded, so they will never contain
    progression or useful items.
    """

    npc: bool = False
    """Whether this item is contingent on killing an NPC or following their quest."""

    prominent: bool = False
    """Whether this is one of few particularly prominent places for items to appear.

    This is a small number of locations (boss drops and progression locations)
    intended to be set as priority locations for players who don't want a lot of
    mandatory checks.

    For bosses with multiple drops, only one should be marked prominent.
    """

    progression: bool = False
    """Whether this location normally contains an item that blocks forward progress."""

    boss: bool = False
    """Whether this location is a reward for defeating a full boss."""

    miniboss: bool = False
    """Whether this location is a reward for defeating a miniboss.
    
    Minibosses are enemies with unique health bars that do not drop memories."""

    drop: bool = False
    """Whether this is an item dropped by a (non-boss) enemy.

    This is automatically set to True if miniboss or hostile is True.
    """

    hostile: bool = False
    """Whether this location is dropped by an enemy or hostile NPC.

    This mostly just covers regular enemies that have guaranteed drops but als includes 
    the Doujun questline NPCs that turn hostile at the end.
    """

    shop: bool = False
    """Whether this location can appear in an NPC's shop.

    Items like Lapp's Set which can appear both in the overworld and in a shop
    should still be tagged as shop.
    """

    conditional: bool = False
    """Whether this location is conditional on a progression item.

    This is used to track locations that won't become available until an unknown amount of time into
    the run, and as such shouldn't have "similar to the base game" items placed in them.
    """

    hidden: bool = False
    """Whether this location is particularly tricky to find.

    This is for players without an encyclopedic knowledge of Sekiro who don't want to get stuck looking
    for some out of the way hidden item.
    """

    headless: bool = False
    """Whether this location is dropped by a headless miniboss."""

    offering_box: bool = False
    """Whether this is an item that moves to the Offering Box after becoming unavailable.

    This is used to track items that could contain some important item that cannot be missed.
    Once the opportunity to acquire the item has passed, it will be placed in the Offering Box.    
    """

    diving: bool = False
    """Whether this location is only accessible via Mibu Breathing Technique
    
    This is used to track locations that are conditional on this progression item specifically,
    and warrant their own rule due to the amount of them.
    """

    @property
    def is_event(self) -> bool:
        """Whether this location represents an event rather than a specific item pickup."""
        return self.default_item_name is None

    def __post_init__(self):
        if not self.is_event:
            self.ap_code = self.ap_code or SekiroLocationData.__location_id
            SekiroLocationData.__location_id += 1
        if self.miniboss or self.hostile: self.drop = True
        if self.diving: self.conditional = True

    def location_groups(self) -> List[str]:
        """The names of location groups this location should appear in.

        This is computed from the properties assigned to this location."""
        names = []
        if self.prominent: names.append("Prominent")
        if self.progression: names.append("Progression")
        if self.boss: names.append("Boss Rewards")
        if self.miniboss: names.append("Miniboss Rewards")
        if self.hostile: names.append("Hostile")
        if self.npc: names.append("Friendly")
        if self.hidden: names.append("Hidden")
        if self.offering_box: names.append("Offering Box")

        default_item = item_dictionary[cast(str, self.default_item_name)]
        names.append({
                         SekiroItemCategory.ESOTERIC_TEXTS: 'Esoteric Texts',
                         SekiroItemCategory.SKILLS: 'Skills',
                         SekiroItemCategory.MISC: "Miscellaneous",
                         SekiroItemCategory.UNIQUE: "Unique",
                         SekiroItemCategory.MEMORIES: "Memories",
                         SekiroItemCategory.CURRENCY: "Currency",
                         SekiroItemCategory.UPGRADE: "Upgrade",
                         SekiroItemCategory.HEALING: "Healing",
                     }[default_item.category])
        if default_item.classification == ItemClassification.progression:
            names.append("Progression")

        return names


class SekiroLocation(Location):
    game: str = "Sekiro: Shadows Die Twice"
    data: SekiroLocationData

    def __init__(
            self,
            player: int,
            data: SekiroLocationData,
            parent: Optional[Region] = None,
            event: bool = False):
        super().__init__(player, data.name, None if event else data.ap_code, parent)
        self.data = data


# Naming conventions:
#
# * The regions in item names should match the physical region where the item is
#   acquired, even if its logical region is different. For example, Irina's
#   inventory appears in the "Undead Settlement" region because she's not
#   accessible until there, but it begins with "FS:" because that's where her
#   items are purchased.
#
# * Avoid using vanilla enemy placements as landmarks, because these are
#   randomized by the enemizer by default. Instead, use generic terms like
#   "mob", "boss", and "miniboss".
#
# * Location descriptions don't need to direct the player to the precise spot.
#   You can assume the player is broadly familiar with Sekiro or willing
#   to look at a vanilla guide. Just give a general area to look in or an idea
#   of what quest a check is connected to. Terseness is valuable: try to keep
#   each location description short enough that the whole line doesn't exceed
#   100 characters.
#
# * Use "[name] drop" for items that require killing an NPC who becomes hostile
#   as part of their normal quest, "kill [name]" for items that require killing
#   them even when they aren't hostile, and just "[name]" for items that are
#   naturally available as part of their quest.
location_tables: Dict[str, List[SekiroLocationData]] = {
    "Ashina Reservoir - Tutorial": [
        SekiroLocationData("AR1: Fistful of Ash - ledge after miniboss", "Fistful of Ash x2", missable=True),
        SekiroLocationData("AR1: Ornamental Letter - in starting well", "Ornamental Letter", missable=True),
        SekiroLocationData("AR1: Pellet - AR gate, miniboss drop", "Pellet", missable=True),
        SekiroLocationData("AR1: Pellet - Moon-View Tower, upper floor", "Pellet", missable=True),
        SekiroLocationData("AR1: Pellet - on ledge under bridge", "Pellet", missable=True),
    ],
    "Dilapidated Temple": [
        SekiroLocationData("DT: Ashina Sake - Emma after healing Sculptor's Dragonrot", "Ashina Sake", missable=True,
                           npc=True, conditional=True),
        SekiroLocationData("DT: Gourd Seed - Fujioka the Info Broker", "Gourd Seed", npc=True, shop=True,
                           conditional=True),
        SekiroLocationData("DT: Hidden Tooth - complete Hanbei's quest", "Hidden Tooth", npc=True, conditional=True),
        SekiroLocationData("DT: Light Coin Purse - behind DT", "Light Coin Purse"),
        SekiroLocationData("DT: Pellet - next to Dilapidated Temple idol", "Pellet x2"),
        SekiroLocationData("DT: Prosthetic Esoteric Text - talk to Sculptor with 3 prosthetic tools",
                           "Prosthetic Esoteric Text", npc=True, conditional=True),
        SekiroLocationData("DT: Sabimaru Memo - Fujioka the Info Broker", "Sabimaru Memo", npc=True, shop=True,
                           conditional=True),
        SekiroLocationData("DT: Shinobi Esoteric Text - talk to Sculptor with 1 skill point", "Shinobi Esoteric Text",
                           npc=True, conditional=True),
        SekiroLocationData("DT: Shinobi Prosthetic - reach Dilapidated Temple", "Shinobi Prosthetic", prominent=True,
                           progression=True),
        SekiroLocationData("DT: Three-story Pagoda Memo - Fujioka the Info Broker", "Three-story Pagoda Memo", npc=True,
                           shop=True, conditional=True),
        SekiroLocationData("DT: Valley Apparitions Memo - Fujioka after miniboss spawn in Guardian Ape's Burrow",
                           "Valley Apparitions Memo", npc=True, shop=True, conditional=True),
    ],
    "Ashina Outskirts": [
        SekiroLocationData("AO1: Ako's Spiritfall - headless cave, miniboss drop", "Ako's Spiritfall", headless=True),
        SekiroLocationData("AO1: Ako's Sugar - back left from Gate Fortress idol", "Ako's Sugar"),
        SekiroLocationData("AO1: Ako's Sugar - right cliff from Outskirts idol, wall cave", "Ako's Sugar", hidden=True),
        SekiroLocationData("AO1: Antidote Powder - lookout building, right room", "Antidote Powder"),
        SekiroLocationData("AO1: Ashina Esoteric Text - Tengu after killing rats", "Ashina Esoteric Text",
                           missable=True, npc=True),
        SekiroLocationData("AO1: Black Gunpowder - right cobblestone platform, enemy drop", "Black Gunpowder",
                           drop=True),
        SekiroLocationData("AO1: Bundled Jizo Statue - ridge inner curve, wall cave", "Bundled Jizo Statue",
                           hidden=True),
        SekiroLocationData("AO1: Ceramic Shard - before the stairs to Battlefield Memorial Mob", "Ceramic Shard"),
        SekiroLocationData("AO1: Ceramic Shard - destroyed house, second floor", "Ceramic Shard x3"),
        SekiroLocationData("AO1: Ceramic Shard - Gate Fortress courtyard house front", "Ceramic Shard"),
        SekiroLocationData("AO1: Ceramic Shard - left of Gate Path idol", "Ceramic Shard x2"),
        SekiroLocationData("AO1: Ceramic Shard - lookout building, left room", "Ceramic Shard x2"),
        SekiroLocationData("AO1: Ceramic Shard - right cliff, broken wall", "Ceramic Shard x2"),
        SekiroLocationData("AO1: Ceramic Shard - under branch after first gate", "Ceramic Shard"),
        SekiroLocationData("AO1: Divine Confetti - slope before headless warning sign", "Divine Confetti"),
        SekiroLocationData("AO1: Divine Grass - lookout building, right room", "Divine Grass"),
        SekiroLocationData("AO1: Fistful of Ash - cliff courtyard, broken hut", "Fistful of Ash x2"),
        SekiroLocationData("AO1: Fistful of Ash - Gate Fortress near dead horse", "Fistful of Ash x2"),
        SekiroLocationData("AO1: Fistful of Ash - in Gyoubu arena", "Fistful of Ash x2"),
        SekiroLocationData("AO1: Fistful of Ash - right of gate leading to Gate Path idol", "Fistful of Ash"),
        SekiroLocationData("AO1: Flame Barrel Memo - Anayama for 20 sen", "Flame Barrel Memo", missable=True, npc=True),
        SekiroLocationData("AO1: Gachiin's Sugar - after shimmy on way to headless cave", "Gachiin's Sugar x2"),
        SekiroLocationData("AO1: Gachiin's Sugar - destroyed house before headless cave shortcut",
                           "Gachiin's Sugar x2"),
        SekiroLocationData("AO1: Gachiin's Sugar - left of Gate Fortress idol", "Gachiin's Sugar"),
        SekiroLocationData("AO1: Gachiin's Sugar - ridge inner curve, tall grass", "Gachiin's Sugar x3"),
        SekiroLocationData("AO1: Gourd Seed - Battlefield Memorial Mob", "Gourd Seed", npc=True, shop=True),
        SekiroLocationData("AO1: Gourd Seed - cliff courtyard, miniboss drop", "Gourd Seed", miniboss=True,
                           offering_box=True),
        SekiroLocationData("AO1: Gourd Seed - lookout building, left room", "Gourd Seed"),
        SekiroLocationData("AO1: Heavy Coin Purse - Gate Fortress courtyard house bottom floor", "Heavy Coin Purse"),
        SekiroLocationData("AO1: Herb Catalogue Scrap - near Gate Fortress idol, enemy drop", "Herb Catalogue Scrap",
                           drop=True),
        SekiroLocationData("AO1: Light Coin Purse - destroyed house, roof", "Light Coin Purse"),
        SekiroLocationData("AO1: Light Coin Purse - room under Inosuke's Mother", "Light Coin Purse",
                           static='00,0:51100140::'),
        SekiroLocationData("AO1: Light Coin Purse - room under Inosuke's Mother", "Light Coin Purse",
                           static='00,0:51100150::'),
        SekiroLocationData("AO1: Light Coin Purse - room under Inosuke's Mother", "Light Coin Purse",
                           static='00,0:51100160::'),
        SekiroLocationData("AO1: Light Coin Purse - second floor of building near Gyoubu arena", "Light Coin Purse"),
        SekiroLocationData("AO1: Mechanical Barrel - Ashina Castle Gate, boss drop", "Mechanical Barrel",
                           prominent=True, boss=True),
        SekiroLocationData("AO1: Memory: Gyoubu Oniwa - Ashina Castle Gate, boss drop", "Memory: Gyoubu Oniwa",
                           boss=True),
        SekiroLocationData("AO1: Mibu Balloon of Wealth - destroyed house, first floor", "Mibu Balloon of Wealth"),
        SekiroLocationData("AO1: Mibu Balloon of Wealth - Gate Fortress courtyard house bottom floor",
                           "Mibu Balloon of Wealth x3"),
        SekiroLocationData("AO1: Mibu Balloon of Wealth - To the left of the 2nd miniboss", "Mibu Balloon of Wealth"),
        SekiroLocationData("AO1: Mibu Possession Balloon - secluded platform, before snake skin",
                           "Mibu Possession Balloon", static='00,0:51100430::'),
        SekiroLocationData("AO1: Mibu Possession Balloon - secluded platform, before snake skin",
                           "Mibu Possession Balloon", static='00,0:51100440::'),
        SekiroLocationData("AO1: Nightjar Monocular - lookout building, at grapple entrance", "Nightjar Monocular"),
        SekiroLocationData("AO1: Oil - Anayama for 20 sen while having Flame Barrel", "Oil x2", missable=True, npc=True,
                           conditional=True),
        SekiroLocationData("AO1: Pellet - after gate closest to Outskirts idol", "Pellet"),
        SekiroLocationData("AO1: Pellet - behind cliffside gate", "Pellet x2"),
        SekiroLocationData("AO1: Pellet - just before Underbridge Valley idol", "Pellet x2"),
        SekiroLocationData("AO1: Pellet - left above wide gate house", "Pellet x3"),
        SekiroLocationData("AO1: Pellet - Left of dead horse in Ashina Castle Fortress", "Pellet x2"),
        SekiroLocationData("AO1: Pellet - left of gate to Gate Path idol", "Pellet"),
        SekiroLocationData("AO1: Pellet - on first floor of building near Gyoubu arena", "Pellet x2"),
        SekiroLocationData("AO1: Pellet - up stairs, before 2nd miniboss", "Pellet"),
        SekiroLocationData("AO1: Phantom Kunai - Anayama the Peddler", "Phantom Kunai", npc=True, shop=True,
                           offering_box=True),
        SekiroLocationData("AO1: Prayer Bead - chest, top floor of Tengu building", "Prayer Bead"),
        SekiroLocationData("AO1: Prayer Bead - courtyard after Stairway idol, miniboss drop", "Prayer Bead",
                           miniboss=True, offering_box=True),
        SekiroLocationData("AO1: Prayer Bead - near Gate Path idol, miniboss drop", "Prayer Bead", miniboss=True,
                           offering_box=True),
        SekiroLocationData("AO1: Prayer Bead - near Stairway idol, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("AO1: Rat Description - agree to help Tengu with rat problem", "Rat Description", npc=True),
        SekiroLocationData("AO1: Robert's Firecrackers - Crow's Bed & Battlefield Memorial Mob",
                           "Robert's Firecrackers", npc=True, shop=True),
        SekiroLocationData("AO1: Scrap Iron - courtyard after lookout building", "Scrap Iron"),
        SekiroLocationData("AO1: Scrap Iron - secluded platform, after snake skin", "Scrap Iron"),
        SekiroLocationData("AO1: Shinobi Medicine Rank 1 - near Stairway idol, miniboss drop",
                           "Shinobi Medicine Rank 1", miniboss=True),
        SekiroLocationData("AO1: Shuriken Wheel - wide gate house second floor", "Shuriken Wheel", offering_box=True),
        SekiroLocationData("AO1: Snap Seed - near palanquin where Great Serpent lies", "Snap Seed x5"),
        SekiroLocationData("AO1: Ungo's Sugar - broken wall above Ashina Outskirts idol", "Ungo's Sugar"),
        SekiroLocationData("AO1: Ungo's Sugar - behind building in Ashina Castle Fortress", "Ungo's Sugar"),
        SekiroLocationData("AO1: Ungo's Sugar - gate house before tall grass", "Ungo's Sugar x2"),
        SekiroLocationData("AO1: Young Lord's Bell Charm - Inosuke's Mother", "Young Lord's Bell Charm", npc=True,
                           progression=True),
    ],
    "Hirata Estate - Young Lord's Bell Charm": [
        SekiroLocationData("HE1: Ako's Sugar - Estate Path, behind first houses", "Ako's Sugar"),
        SekiroLocationData("HE1: Antidote Powder - woman inside unpillaged house", "Antidote Powder x2", npc=True),
        SekiroLocationData("HE1: Bulging Coin Purse - side path before cave, enemy drop", "Bulging Coin Purse",
                           drop=True, conditional=True),
        SekiroLocationData("HE1: Bundled Jizo Statue - bamboo path behind Anayama", "Bundled Jizo Statue"),
        SekiroLocationData("HE1: Ceramic Shard - beside Estate Path idol", "Ceramic Shard x2"),
        SekiroLocationData("HE1: Ceramic Shard - bonfire houses, base of tree", "Ceramic Shard x3"),
        SekiroLocationData("HE1: Ceramic Shard - Main Hall, island in the marsh", "Ceramic Shard", conditional=True),
        SekiroLocationData("HE1: Contact Medicine - next to waterfall before pagoda entrance", "Contact Medicine",
                           conditional=True),
        SekiroLocationData("HE1: Divine Confetti - Audience Chamber, behind shinobi door far left",
                           "Divine Confetti x2", conditional=True),
        SekiroLocationData("HE1: Divine Confetti - Main Hall, inside large building before marsh", "Divine Confetti x2",
                           conditional=True),
        SekiroLocationData("HE1: Divine Grass - Pot Noble Harunaga", "Divine Grass", npc=True, shop=True),
        SekiroLocationData("HE1: Dousing Powder - Audience Chamber, left room in left corner", "Dousing Powder x2",
                           conditional=True),
        SekiroLocationData("HE1: Dousing Powder - grapple from first archer at Bamboo Thicket Slope",
                           "Dousing Powder x2", conditional=True),
        SekiroLocationData("HE1: Dousing Powder - Main Hall, inside large building before marsh", "Dousing Powder",
                           conditional=True),
        SekiroLocationData("HE1: Dousing Powder - near bandits' bonfire", "Dousing Powder"),
        SekiroLocationData("HE1: Dousing Powder - turn around before crossing first bridge", "Dousing Powder x2"),
        SekiroLocationData("HE1: Fistful of Ash - after Bamboo Thicket Slope bridge on right", "Fistful of Ash"),
        SekiroLocationData("HE1: Fistful of Ash - before shortcut door", "Fistful of Ash x3"),
        SekiroLocationData("HE1: Fistful of Ash - cliff bottom, beside dying Nightjar", "Fistful of Ash x2"),
        SekiroLocationData("HE1: Fistful of Ash - left of bandits' bonfire near tree", "Fistful of Ash"),
        SekiroLocationData("HE1: Flame Barrel - near bandits' bonfire", "Flame Barrel"),
        SekiroLocationData("HE1: Floating Passage Text - Pot Noble Harunaga", "Floating Passage Text", npc=True,
                           shop=True, conditional=True),
        SekiroLocationData("HE1: Gokan's Sugar - right after Estate Path shortcut", "Gokan's Sugar"),
        SekiroLocationData("HE1: Hidden Temple Key - Owl in burning courtyard", "Hidden Temple Key", npc=True,
                           prominent=True, progression=True),
        SekiroLocationData("HE1: Lapis Lazuli - Pot Noble Harunaga after Truly Precious Bait", "Lapis Lazuli",
                           missable=True, npc=True, conditional=True, diving=True),
        SekiroLocationData("HE1: Light Coin Purse - Audience Chamber, behind shinobi door", "Light Coin Purse",
                           conditional=True),
        SekiroLocationData("HE1: Light Coin Purse - left house roof after shortcut", "Light Coin Purse"),
        SekiroLocationData("HE1: Light Coin Purse - Main Hall, left building after marsh", "Light Coin Purse",
                           conditional=True),
        SekiroLocationData("HE1: Light Coin Purse - on rocks near Pot Noble Harunaga", "Light Coin Purse"),
        SekiroLocationData("HE1: Light Count Purse - left of buddha shrine", "Light Coin Purse"),
        SekiroLocationData("HE1: Mask Fragment: Right - Pot Noble Harunaga", "Mask Fragment: Right", npc=True,
                           shop=True, conditional=True),
        SekiroLocationData("HE1: Memory: Lady Butterfly - Hidden Temple, boss drop", "Memory: Lady Butterfly",
                           boss=True, conditional=True),
        SekiroLocationData("HE1: Mibu Balloon of Soul - Audience Chamber, room left of idol", "Mibu Balloon of Soul",
                           conditional=True),
        SekiroLocationData("HE1: Mibu Balloon of Soul - side path before cave", "Mibu Balloon of Soul",
                           conditional=True),
        SekiroLocationData("HE1: Mibu Balloon of Wealth - Audience Chamber, behind shinobi door",
                           "Mibu Balloon of Wealth", conditional=True),
        SekiroLocationData("HE1: Mibu Balloon of Wealth - near bandits' bonfire", "Mibu Balloon of Wealth"),
        SekiroLocationData("HE1: Mibu Possession Balloon - boat near Pot Noble Harunaga", "Mibu Possession Balloon"),
        SekiroLocationData("HE1: Mibu Possession Balloon - left of gate to Bamboo Thicket Slope idol",
                           "Mibu Possession Balloon"),
        SekiroLocationData("HE1: Mibu Possession Balloon - side path before cave in crouch opening",
                           "Mibu Possession Balloon", conditional=True, hidden=True),
        SekiroLocationData("HE1: Mist Raven's Feathers - three-story pagoda", "Mist Raven's Feathers", progression=True,
                           conditional=True),
        SekiroLocationData("HE1: Oil - Audience Chamber, left hallway before shinobi door", "Oil", conditional=True),
        SekiroLocationData("HE1: Oil - before Bamboo Thicket Slope bridge", "Oil"),
        SekiroLocationData("HE1: Oil - Main Hall, between well and idol", "Oil x2", conditional=True),
        SekiroLocationData("HE1: Pellet - Audience Chamber, left room on right wall", "Pellet x2", conditional=True),
        SekiroLocationData("HE1: Pellet - behind start", "Pellet x2"),
        SekiroLocationData("HE1: Pellet - first houses, inside largest house", "Pellet x2"),
        SekiroLocationData("HE1: Pellet - left house after shortcut near well", "Pellet"),
        SekiroLocationData("HE1: Pellet - near bandits' bonfire", "Pellet x2"),
        SekiroLocationData("HE1: Pellet - right of gate to Bamboo Thicket Slope idol", "Pellet x2"),
        SekiroLocationData("HE1: Pellet - side path before cave", "Pellet x2", conditional=True),
        SekiroLocationData("HE1: Prayer Bead - Audience Chamber, chest behind shinobi door", "Prayer Bead",
                           conditional=True),
        SekiroLocationData("HE1: Prayer Bead - before Bamboo Thicket Slope, miniboss drop", "Prayer Bead",
                           miniboss=True),
        SekiroLocationData("HE1: Prayer Bead - entrance to Audience Chamber, miniboss drop", "Prayer Bead",
                           miniboss=True, conditional=True),
        SekiroLocationData("HE1: Sakura Droplet - Hidden Temple, boss drop", "Sakura Droplet", prominent=True,
                           boss=True, conditional=True),
        SekiroLocationData("HE1: Scrap Iron - guarding three-storey pagoda, enemy drop", "Scrap Iron", drop=True,
                           conditional=True),
        SekiroLocationData("HE1: Shinobi Axe of the Monkey - buddha shrine", "Shinobi Axe of the Monkey"),
        SekiroLocationData("HE1: Snap Seed - Audience Chamber, Inosuke", "Snap Seed", conditional=True),
        SekiroLocationData("HE1: Treasure Carp Scale - behind rock before crossing first bridge",
                           "Treasure Carp Scale"),
        SekiroLocationData("HE1: Truly Precious Bait - Pot Noble Harunaga after trading 6 scales", "Truly Precious Bait",
                           missable=True, npc=True, conditional=True),
        SekiroLocationData("HE1: Ungo's Sugar - left big house after shortcut", "Ungo's Sugar x3"),
        SekiroLocationData("HE1: Ungo's Sugar - left of Estate Path, over wall", "Ungo's Sugar x3"),
        SekiroLocationData("HE1: Unrefined Sake - entrance to Audience Chamber, miniboss drop", "Unrefined Sake",
                           missable=True, conditional=True),
        SekiroLocationData("HE1: Withered Red Gourd - Pot Noble Harunaga", "Withered Red Gourd", npc=True, shop=True)
    ],
    "Ashina Castle": [
        SekiroLocationData("AC1: Ako's Sugar - any Old Praying Woman, pop 2 balloons", "Ako's Sugar", missable=True),
        SekiroLocationData("AC1: Ako's Sugar - before Bull arena, on left cliffside, behind wall", "Ako's Sugar x2",
                           hidden=True),
        SekiroLocationData("AC1: Ako's Sugar - Upper Tower, map room", "Ako's Sugar"),
        SekiroLocationData("AC1: Anti-Air Deathblow Text - Blackhat Badger", "Anti-air Deathblow Text", npc=True,
                           shop=True, offering_box=True),
        SekiroLocationData("AC1: Black Gunpowder - destroyed bridge to Ashina Outskirts", "Black Gunpowder"),
        SekiroLocationData("AC1: Black Gunpowder - outside building at Abandoned Dungeon Entrance", "Black Gunpowder"),
        SekiroLocationData("AC1: Black Gunpowder - Tengu rat quest enemy drop", "Black Gunpowder"),
        SekiroLocationData("AC1: Bloodsmoke Ninjutsu - Upper Tower roof, boss drop", "Bloodsmoke Ninjutsu", boss=True),
        SekiroLocationData("AC1: Ceramic Shard - base of stairs after Ashina Castle Gate idol", "Ceramic Shard"),
        SekiroLocationData("AC1: Ceramic Shard - bird's nest on rooftop of buildings on right", "Ceramic Shard x2"),
        SekiroLocationData("AC1: Ceramic Shard - bird's nest before Upper Tower - Antechamber idol", "Ceramic Shard"),
        SekiroLocationData("AC1: Ceramic Shard - Old Grave, courtyard near Blackhat Badger", "Ceramic Shard"),
        SekiroLocationData("AC1: Ceramic Shard - right of main stairway next to Ashina Castle idol", "Ceramic Shard"),
        SekiroLocationData("AC1: Ceramic Shard - right of stairway to Upper Tower - Ashina Dojo idol", "Ceramic Shard"),
        SekiroLocationData("AC1: Divine Confetti - any Old Praying Woman, pop 3 balloons", "Divine Confetti",
                           missable=True),
        SekiroLocationData("AC1: Divine Grass - chest at top of main stairway", "Divine Grass"),
        SekiroLocationData("AC1: Dragon's Blood Droplet - Old Grave, near graves", "Dragon's Blood Droplet"),
        SekiroLocationData("AC1: Eel Liver - Ashina Dojo", "Eel Liver x3"),
        SekiroLocationData("AC1: Eel Liver - basement, side room with chest", "Eel Liver x2"),
        SekiroLocationData("AC1: Eel Liver - lower floor in Isshin's watchtower", "Eel Liver x2"),
        SekiroLocationData("AC1: Eel Liver - small shrine across from Great Serpent Shrine", "Eel Liver x3"),
        SekiroLocationData("AC1: Fistful of Ash - before Bull arena, corner house at tree", "Fistful of Ash x2"),
        SekiroLocationData("AC1: Fistful of Ash - courtyard right of Ashina Castle idol", "Fistful of Ash x3"),
        SekiroLocationData("AC1: Fistful of Ash - between window and Upper Tower - Antechamber idol", "Fistful of Ash"),
        SekiroLocationData("AC1: Fistful of Ash - Old Grave, courtyard near Blackhat Badger building",
                           "Fistful of Ash"),
        SekiroLocationData("AC1: Fragrant Flower Note - talk to Kuro about flower", "Fragrant Flower Note",
                           missable=True, npc=True),
        SekiroLocationData("AC1: Gachiin's Sugar - at tree near Bull arena walls", "Gachiin's Sugar x2"),
        SekiroLocationData("AC1: Gachiin's Sugar - basement, side room with chest", "Gachiin's Sugar x2"),
        SekiroLocationData("AC1: Gachiin's Sugar - bird's nest on roof near Isshin's watchtower", "Gachiin's Sugar"),
        SekiroLocationData("AC1: Gachiin's Sugar - Old Grave, bird's nest close to idol", "Gachiin's Sugar"),
        SekiroLocationData("AC1: Gachiin's Sugar - Old Grave, courtyard near Blackhat Badger building",
                           "Gachiin's Sugar"),
        SekiroLocationData("AC1: Gokan's Sugar - basement, side room with chest", "Gokan's Sugar"),
        SekiroLocationData("AC1: Gokan's Sugar - room with Upper Tower - Ashina Dojo idol", "Gokan's Sugar"),
        SekiroLocationData("AC1: Gourd Seed - chest near Antechamber idol", "Gourd Seed"),
        SekiroLocationData("AC1: Gun Fort Shrine Key - library in Kuro's Room after talking to Isshin",
                           "Gun Fort Shrine Key", progression=True),
        SekiroLocationData("AC1: Heavy Coin Purse - before Serpent Shrine bridge, enemy drop", "Heavy Coin Purse",
                           drop=True),
        SekiroLocationData("AC1: Heavy Coin Purse - underwater, near headless in rear moat", "Heavy Coin Purse",
                           static='02,0:51110480::', conditional=True, diving=True),
        SekiroLocationData("AC1: Heavy Coin Purse - underwater, near headless in rear moat", "Heavy Coin Purse",
                           static='02,0:51110490::', conditional=True, diving=True),
        SekiroLocationData("AC1: Heavy Coin Purse - underwater, near headless in rear moat", "Heavy Coin Purse",
                           static='02,0:51110800::', conditional=True, diving=True),
        SekiroLocationData("AC1: Heavy Coin Purse - Upper Tower, past shinobi door", "Heavy Coin Purse", hidden=True),
        SekiroLocationData("AC1: Heavy Coin Purse - wagon before Dungeon Memorial Mob", "Heavy Coin Purse"),
        SekiroLocationData("AC1: Immortal Severance Scrap - talk to Emma after Kuro", "Immortal Severance Scrap",
                           missable=True, npc=True, conditional=True),
        SekiroLocationData("AC1: Immortal Severance Text - talk to Kuro", "Immortal Severance Text", npc=True),
        SekiroLocationData("AC1: Iron Fortress - Blackhat Badger", "Iron Fortress", npc=True, shop=True,
                           offering_box=True),
        SekiroLocationData("AC1: Isshin's Letter - Isshin's watchtower before top floor boss", "Isshin's Letter",
                           missable=True),
        SekiroLocationData("AC1: Light Coin Purse - bird's nest near Castle Tower Lookout idol", "Light Coin Purse"),
        SekiroLocationData("AC1: Light Coin Purse - left before bridge to ADG in house", "Light Coin Purse"),
        SekiroLocationData("AC1: Light Coin Purse - Old Grave, courtyard near Blackhat Badger building",
                           "Light Coin Purse"),
        SekiroLocationData("AC1: Light Coin Purse - top level of building near stairs to Bull arena",
                           "Light Coin Purse"),
        SekiroLocationData("AC1: Light Coin Purse - Upper Tower, past shinobi door", "Light Coin Purse"),
        SekiroLocationData("AC1: Memory: Genichiro - Upper Tower roof, boss drop", "Memory: Genichiro", prominent=True,
                           boss=True),
        SekiroLocationData("AC1: Mibu Balloon of Spirit - room before Serpent Shrine idol", "Mibu Balloon of Spirit"),
        SekiroLocationData("AC1: Mibu Balloon of Wealth - alcove right near end of main stairway",
                           "Mibu Balloon of Wealth"),
        SekiroLocationData("AC1: Mibu Balloon of Wealth - stairway to Ashina Dojo idol", "Mibu Balloon of Wealth"),
        SekiroLocationData("AC1: Mibu Possession Balloon - end of Serpent Shrine bridge", "Mibu Possession Balloon x2"),
        SekiroLocationData("AC1: Mibu Possession Balloon - left from Ashina Castle idol and through building",
                           "Mibu Possession Balloon"),
        SekiroLocationData("AC1: Mibu Possession Balloon - under Serpent Shrine bridge", "Mibu Possession Balloon"),
        SekiroLocationData("AC1: Mibu Possession Balloon - underwater, near Serpent Shrine bridge",
                           "Mibu Possession Balloon x2", conditional=True, diving=True),
        SekiroLocationData("AC1: Nightjar Beacon Memo - Fujioka after killing samurais", "Nightjar Beacon Memo",
                           missable=True, npc=True),
        SekiroLocationData("AC1: Okami's Ancient Text - show Lotus of the Palace to Kuro", "Okami's Ancient Text",
                           missable=True, npc=True, conditional=True),
        SekiroLocationData("AC1: Page's Diary - talk to Kuro after agreeing to Immortal Severence", "Page's Diary",
                           missable=True, npc=True),
        SekiroLocationData("AC1: Pellet - Ashina Dojo, side room", "Pellet"),
        SekiroLocationData("AC1: Pellet - at tree with eavesdrop near Tengu quest enemy", "Pellet x2"),
        SekiroLocationData("AC1: Pellet - before AR gate", "Pellet"),
        SekiroLocationData("AC1: Pellet - bird's nest on rooftop before kite Ninja roof ", "Pellet"),
        SekiroLocationData("AC1: Pellet - Isshin's dojo, stairs to Isshin", "Pellet x2"),
        SekiroLocationData("AC1: Pellet - Upper Tower, corner room near map", "Pellet x2"),
        SekiroLocationData("AC1: Prayer Bead - Ashina Castle Gate, miniboss drop", "Prayer Bead", missable=True,
                           miniboss=True),
        SekiroLocationData("AC1: Prayer Bead - Ashina Dojo, miniboss drop", "Prayer Bead", miniboss=True,
                           offering_box=True),
        SekiroLocationData("AC1: Prayer Bead - up stairs from Ashina Castle idol, miniboss drop", "Prayer Bead",
                           miniboss=True, offering_box=True),
        SekiroLocationData("AC1: Prayer Bead - Upper Tower, chest past shinobi door", "Prayer Bead"),
        SekiroLocationData("AC1: Sabimaru - basement, chest", "Sabimaru"),
        SekiroLocationData("AC1: Scrap Iron - before Bull arena, hidden behind corner house", "Scrap Iron"),
        SekiroLocationData("AC1: Scrap Iron - ledge on right overlooking Ashina Castle idol", "Scrap Iron"),
        SekiroLocationData("AC1: Scrap Iron - left from Ashina Castle idol and through building", "Scrap Iron"),
        SekiroLocationData("AC1: Scrap Iron - on ledge across moat with underwater headless", "Scrap Iron x2"),
        SekiroLocationData("AC1: Scrap Iron - on stone near Bull arena walls", "Scrap Iron"),
        SekiroLocationData("AC1: Scrap Iron - Upper Tower, map room", "Scrap Iron"),
        SekiroLocationData("AC1: Scrap Magnetite - Ashina Dojo, side room", "Scrap Magnetite"),
        SekiroLocationData("AC1: Scrap Magnetite - before Bull arena, enemy drop", "Scrap Magnetite", drop=True),
        SekiroLocationData("AC1: Scrap Magnetite - behind statue in Kuro's Room", "Scrap Magnetite"),
        SekiroLocationData("AC1: Shinobi Medicine Rank 2 - Ashina Castle Gate, miniboss drop",
                           "Shinobi Medicine Rank 2", missable=True, miniboss=True),
        SekiroLocationData("AC1: Sweet Rice Ball - Kuro after Rice for Kuro", "Sweet Rice Ball x2", missable=True,
                           npc=True, conditional=True),
        SekiroLocationData("AC1: Treasure Carp Scale - underwater, below Ashina Castle idol", "Treasure Carp Scale",
                           conditional=True, diving=True),
        SekiroLocationData("AC1: Ungo's Spiritfall - underwater, headless drop", "Ungo's Spiritfall", conditional=True,
                           headless=True, diving=True),
        SekiroLocationData("AC1: Ungo's Sugar - any Old Praying Woman, pop 1 balloon", "Ungo's Sugar", missable=True),
        SekiroLocationData("AC1: Ungo's Sugar - bird's nest, tower roof outside Upper Tower - Antechamber idol",
                           "Ungo's Sugar"),
        SekiroLocationData("AC1: Ungo's Sugar - bird's nest, roof of Blackhat Badger building", "Ungo's Sugar x2"),
        SekiroLocationData("AC1: Unrefined Sake - ask Isshin about Mortal Blade without having it", "Unrefined Sake",
                           missable=True, npc=True),
        SekiroLocationData("AC1: Yashariku's Sugar - underwater, near headless against castle wall",
                           "Yashariku's Sugar", conditional=True, diving=True),
        SekiroLocationData("AC1 -> SV", None),
    ],
    "Ashina Reservoir - Revisit": [
        SekiroLocationData("AR2: Bundled Jizo Statue - Moon-View Tower, red balcony", "Bundled Jizo Statue"),
        SekiroLocationData("AR2: Ceramic Shard - under gatehouse", "Ceramic Shard x2", hidden=True),
        SekiroLocationData("AR2: Fistful of Ash - stairs leading to gatehouse", "Fistful of Ash"),
        SekiroLocationData("AR2: Gatehouse Key - bridge leading to Abandoned Dungeon, enemy drop", "Gatehouse Key",
                           drop=True),
        SekiroLocationData("AR2: Gyoubu's Broken Horn - gatehouse chest", "Gyoubu's Broken Horn", conditional=True,
                           offering_box=True),
        SekiroLocationData("AR2: Heavy Coin Purse - door left of Secret Passage entrance", "Heavy Coin Purse"),
        SekiroLocationData("AR2: Heavy Coin Purse - next to gatehouse chest", "Heavy Coin Purse", conditional=True),
        SekiroLocationData("AR2: Mibu Balloon of Soul - underwater, starting well", "Mibu Balloon of Soul",
                           conditional=True, diving=True),
        SekiroLocationData("AR2: Mibu Balloon of Spirit - in the moat", "Mibu Balloon of Spirit"),
        SekiroLocationData("AR2: Pellet - broken cart in yard", "Pellet"),
        SekiroLocationData("AR2: Prayer Bead - Moon-View Tower, miniboss drop", "Prayer Bead", miniboss=True,
                           offering_box=True),
        SekiroLocationData("AR2: Prayer Bead - starting well, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("AR2: Scrap Iron - door left of Secret Passage entrance", "Scrap Iron"),
        SekiroLocationData("AR2: Scrap Iron - grapple up towards Abandoned Dungeon from well", "Scrap Iron"),
        SekiroLocationData("AR2: Scrap Iron - tree beside Moon-View Tower", "Scrap Iron"),
        SekiroLocationData("AR2: Scrap Magnetite - starting well, miniboss drop", "Scrap Magnetite x2", missable=True),
    ],
    "Abandoned Dungeon": [
        SekiroLocationData("ADG: Academics' Red Lump - red-eyed Doujun, enemy drop", "Academics' Red Lump",
                           missable=True, conditional=True),
        SekiroLocationData("ADG: Ako's Sugar - boat in Underground Waterway", "Ako's Sugar x2"),
        SekiroLocationData("ADG: Bite Down - thin cave connecting ADG to Bottomless Hole", "Bite Down"),
        SekiroLocationData("ADG: Black Gunpowder - in an alcove in miniboss arena", "Black Gunpowder"),
        SekiroLocationData("ADG: Black Gunpowder - island in Underground Waterway", "Black Gunpowder"),
        SekiroLocationData("ADG: Bulging Coin Purse - stalagmite near Bottomless Hole idol", "Bulging Coin Purse"),
        SekiroLocationData("ADG: Ceramic Shard - underwater, in Underground Waterway", "Ceramic Shard",
                           conditional=True, diving=True),
        SekiroLocationData("ADG: Ceremonial Tanto - near Bottomless Hole, miniboss drop", "Ceremonial Tanto",
                           miniboss=True),
        SekiroLocationData("ADG: Dosaku's Note - Doujun's cell", "Dosaku's Note", conditional=True),
        SekiroLocationData("ADG: Fistful of Ash - after Bottomless Hole, before dropping to Poison Pool",
                           "Fistful of Ash x2"),
        SekiroLocationData("ADG: Light Coin Purse - island in Underground Waterway", "Light Coin Purse"),
        SekiroLocationData("ADG: Light Coin Purse - underwater, in Underground Waterway", "Light Coin Purse",
                           static='04,0:51300150::', conditional=True, diving=True),
        SekiroLocationData("ADG: Light Coin Purse - underwater, in Underground Waterway", "Light Coin Purse",
                           static='04,0:51300260::', conditional=True, diving=True),
        SekiroLocationData("ADG: Light Coin Purse - underwater, in Underground Waterway", "Light Coin Purse",
                           static='04,0:51300270::', conditional=True, diving=True),
        SekiroLocationData("ADG: Lump of Fat Wax - Doujun after sending subject", "Lump of Fat Wax x3", missable=True,
                           npc=True, conditional=True),
        SekiroLocationData("ADG: Lump of Grave Wax - Doujun for Red Carp Eyes", "Lump of Grave Wax x2", missable=True,
                           npc=True, conditional=True),
        SekiroLocationData("ADG: Mask Fragment: Dragon - Dungeon Memorial Mob", "Mask Fragment: Dragon", npc=True,
                           shop=True),
        SekiroLocationData("ADG: Mibu Balloon of Soul - grapple after underwater path to Doujun's cell",
                           "Mibu Balloon of Soul", conditional=True, diving=True),
        SekiroLocationData("ADG: Mibu Balloon of Soul - stalagmite in miniboss arena", "Mibu Balloon of Soul x3"),
        SekiroLocationData("ADG: Mibu Balloon of Soul - Bottomless Hole, top platform after falling",
                           "Mibu Balloon of Soul x2"),
        SekiroLocationData("ADG: Mibu Balloon of Soul - wooden planks above miniboss arena", "Mibu Balloon of Soul"),
        SekiroLocationData("ADG: Oil - in cricket pit", "Oil", static='04,0:51300050::'),
        SekiroLocationData("ADG: Oil - in cricket pit", "Oil", static='04,0:51300070::'),
        SekiroLocationData("ADG: Pacifying Agent - along right wall from Ashina Castle", "Pacifying Agent x3"),
        SekiroLocationData("ADG: Pacifying Agent - Doujun's cell", "Pacifying Agent x5", conditional=True),
        SekiroLocationData("ADG: Pacifying Agent - first cell right from Ashina Castle", "Pacifying Agent x2"),
        SekiroLocationData("ADG: Pacifying Agent - island in Underground Waterway", "Pacifying Agent x2"),
        SekiroLocationData("ADG: Pacifying Agent - small platform above miniboss arena", "Pacifying Agent"),
        SekiroLocationData("ADG: Prayer Bead - Dungeon Memorial Mob", "Prayer Bead", npc=True, shop=True),
        SekiroLocationData("ADG: Red Lump - corpse before Underground Waterway idol", "Red Lump"),
        SekiroLocationData("ADG: Red Lump - red-eyed Jinzaemon/Kotaro, enemy drop", "Red Lump", missable=True,
                           conditional=True),
        SekiroLocationData("ADG: Rotting Prisoner's Note - first cell left from Ashina Castle",
                           "Rotting Prisoner's Note"),
        SekiroLocationData("ADG: Scrap Iron - ramp after Underground Waterway idol", "Scrap Iron"),
        SekiroLocationData("ADG: Scrap Magnetite - next to wall in miniboss arena", "Scrap Magnetite"),
        SekiroLocationData("ADG: Surgeon's Bloody Letter - start Doujun's quest", "Surgeon's Bloody Letter",
                           missable=True, npc=True),
        SekiroLocationData("ADG: Surgeon's Stained Letter - Doujun requests Red Carp Eyes", "Surgeon's Stained Letter",
                           missable=True, npc=True, conditional=True),
        SekiroLocationData("ADG -> ST", None),
        SekiroLocationData("ADG -> PP", None),
    ],
    "Senpou Temple, Mt. Kongo": [
        SekiroLocationData("ST: Ako's Sugar - cliff left of Main Hall", "Ako's Sugar"),
        SekiroLocationData("ST: Ako's Sugar - cricket building entrance", "Ako's Sugar"),
        SekiroLocationData("ST: Ako's Sugar - stairs before cricket building", "Ako's Sugar"),
        SekiroLocationData("ST: Antidote Powder - cliffside right of cricket building, 3-item group",
                           "Antidote Powder x2",
                           static='07,0:52000080::'),
        SekiroLocationData("ST: Antidote Powder - cliffside right of cricket building, 3-item group", "Antidote Powder",
                           static='07,0:52000830::'),
        SekiroLocationData("ST: Antidote Powder - left wall before broken bridge", "Antidote Powder"),
        SekiroLocationData("ST: Black Gunpowder - cliffside temple", "Black Gunpowder x2", static='07,0:52000350::'),
        SekiroLocationData("ST: Black Gunpowder - cliffside temple", "Black Gunpowder", static='07,0:52000540::'),
        SekiroLocationData("ST: Black Gunpowder - Main Hall, right wing", "Black Gunpowder"),
        SekiroLocationData("ST: Black Gunpowder - room before Bell Demon's Temple idol", "Black Gunpowder"),
        SekiroLocationData("ST: Breath of Nature: Shadow - roof bridge, miniboss drop", "Breath of Nature: Shadow",
                           miniboss=True),
        SekiroLocationData("ST: Bulging Coin Purse - kill 3 enemies outside Main Hall", "Bulging Coin Purse",
                           drop=True),
        SekiroLocationData("ST: Bundled Jizo Statue - amid statues left of Main Hall idol", "Bundled Jizo Statue"),
        SekiroLocationData("ST: Ceramic Shard - behind courtyard building", "Ceramic Shard x2"),
        SekiroLocationData("ST: Ceramic Shard - cricket building, left of exit window", "Ceramic Shard x4"),
        SekiroLocationData("ST: Ceramic Shard - nest before Shugendo Memorial Mob", "Ceramic Shard x3"),
        SekiroLocationData("ST: Ceramic Shard - rooftop in front of Temple Grounds idol", "Ceramic Shard x2"),
        SekiroLocationData("ST: Dragon's Blood Droplet - Main Hall, held by statue", "Dragon's Blood Droplet"),
        SekiroLocationData("ST: Fistful of Ash - balcony overlooking Carp pond", "Fistful of Ash x3"),
        SekiroLocationData("ST: Fistful of Ash - beside bonfire on slope to Main Hall", "Fistful of Ash x5",
                           hidden=True),
        SekiroLocationData("ST: Fistful of Ash - ground before cricket building entrance", "Fistful of Ash"),
        SekiroLocationData("ST: Five-color Rice - Shugendo Memorial Mob", "Five-color Rice", npc=True, shop=True),
        SekiroLocationData("ST: Frozen Tears - Divine Child for both Serpent Viscera after first Invasion",
                           "Frozen Tears",
                           missable=True, npc=True, progression=True, conditional=True),
        SekiroLocationData("ST: Gachiin's Sugar - end of broken bridge", "Gachiin's Sugar"),
        SekiroLocationData("ST: Gachiin's Sugar - in area with kite mechanism", "Gachiin's Sugar"),
        SekiroLocationData("ST: Gachiin's Sugar - left of Senpou Temple, Mt. Kongo idol building", "Gachiin's Sugar"),
        SekiroLocationData("ST: Gachiin's Sugar - separate stone pillar in Shugendo", "Gachiin's Sugar"),
        SekiroLocationData("ST: Gokan's Sugar - below Temple Grounds idol", "Gokan's Sugar"),
        SekiroLocationData("ST: Gokan's Sugar - cliffside temple", "Gokan's Sugar"),
        SekiroLocationData("ST: Gokan's Sugar - cricket building, left of exit window", "Gokan's Sugar"),
        SekiroLocationData("ST: Gokan's Sugar - slope leading to Main Hall, ledge above tall grass", "Gokan's Sugar"),
        SekiroLocationData("ST: Gourd Seed - cricket building, main room", "Gourd Seed"),
        SekiroLocationData("ST: Heavy Coin Purse - along White Pinwheel path", "Heavy Coin Purse"),
        SekiroLocationData("ST: Heavy Coin Purse - broken bridge, enemy drop", "Heavy Coin Purse", drop=True),
        SekiroLocationData("ST: Heavy Coin Purse - elevated cliff right of cricket building entrance",
                           "Heavy Coin Purse"),
        SekiroLocationData("ST: Heavy Coin Purse - grapple room before Bell Demon's Temple idol", "Heavy Coin Purse"),
        SekiroLocationData("ST: Heavy Coin Purse - other side of broken bridge", "Heavy Coin Purse"),
        SekiroLocationData("ST: Holy Chapter: Dragon's Return - cave, on blue-robed monk after Holy Chapter: Infested",
                           "Holy Chapter: Dragon's Return", conditional=True),
        SekiroLocationData("ST: Holy Chapter: Infested - underwater, Carp pond", "Holy Chapter: Infested", npc=True,
                           conditional=True, diving=True),
        SekiroLocationData("ST: Light Coin Purse - cliffside right of cricket building, 3-item group",
                           "Light Coin Purse"),
        SekiroLocationData("ST: Light Coin Purse - inner courtyard, right side", "Light Coin Purse"),
        SekiroLocationData("ST: Light Coin Purse - nest on large tree after cricket building exit", "Light Coin Purse"),
        SekiroLocationData("ST: Light Coin Purse - on roof of mini gate at area start", "Light Coin Purse",
                           hidden=True),
        SekiroLocationData("ST: Lump of Fat Wax - behind cricket building shrine", "Lump of Fat Wax"),
        SekiroLocationData("ST: Lump of Fat Wax - courtyard, inside building", "Lump of Fat Wax"),
        SekiroLocationData("ST: Lump of Fat Wax - Main Hall, behind large statue", "Lump of Fat Wax"),
        SekiroLocationData("ST: Memory: Screen Monkeys - Illusive Hall, boss drop", "Memory: Screen Monkeys",
                           boss=True),
        SekiroLocationData("ST: Mibu Balloon of Spirit - after Sunken Valley Cavern idol", "Mibu Balloon of Spirit x3",
                           conditional=True),
        SekiroLocationData("ST: Mibu Balloon of Spirit - base of slope that leads to Main Hall",
                           "Mibu Balloon of Spirit x2"),
        SekiroLocationData("ST: Mibu Balloon of Spirit - cave, shallow section with puddle", "Mibu Balloon of Spirit"),
        SekiroLocationData("ST: Mibu Balloon of Spirit - cricket building, right of exit", "Mibu Balloon of Spirit"),
        SekiroLocationData("ST: Mibu Balloon of Spirit - in area with kite mechanism", "Mibu Balloon of Spirit"),
        SekiroLocationData("ST: Mibu Balloon of Spirit - on path leading to other side of broken bridge",
                           "Mibu Balloon of Spirit", static='07,0:52000120::'),
        SekiroLocationData("ST: Mibu Balloon of Spirit - on path leading to other side of broken bridge",
                           "Mibu Balloon of Spirit", static='07,0:52000130::'),
        SekiroLocationData("ST: Mibu Balloon of Spirit - on path leading to other side of broken bridge",
                           "Mibu Balloon of Spirit", static='07,0:52000370::'),
        SekiroLocationData("ST: Mibu Balloon of Spirit - Shugendo, cave path", "Mibu Balloon of Spirit"),
        SekiroLocationData("ST: Mibu Possession Balloon - on path before cricket building",
                           "Mibu Possession Balloon x2"),
        SekiroLocationData("ST: Mibu Possession Balloon - tree above other side of broken bridge",
                           "Mibu Possession Balloon", hidden=True),
        SekiroLocationData("ST: Monkey Booze - building before Bell Demon's Temple idol", "Monkey Booze"),
        SekiroLocationData("ST: Mortal Blade - Divine Child", "Mortal Blade", npc=True, prominent=True,
                           progression=True),
        SekiroLocationData("ST: Pacifying Agent - near left wall before cricket building", "Pacifying Agent"),
        SekiroLocationData("ST: Pellet - behind Inner Sanctum building", "Pellet x2"),
        SekiroLocationData("ST: Pellet - Main Hall, left wing", "Pellet"),
        SekiroLocationData("ST: Pellet - on path to cricket building", "Pellet"),
        SekiroLocationData("ST: Pellet - other side of broken bridge", "Pellet"),
        SekiroLocationData("ST: Pellet - under grapple spot to Shugendo idol", "Pellet"),
        SekiroLocationData("ST: Pellet - under tree after cave", "Pellet x2"),
        SekiroLocationData("ST: Persimmon - other side of Broken Bridge at leafless tree", "Persimmon"),
        SekiroLocationData("ST: Prayer Bead - cliffside temple, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("ST: Prayer Bead - roof bridge,  miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("ST: Prayer Bead - underwater, Carp pond", "Prayer Bead", conditional=True, diving=True),
        SekiroLocationData("ST: Puppeteer Ninjutsu - Illusive Hall, boss drop", "Puppeteer Ninjutsu", prominent=True,
                           progression=True, boss=True),
        SekiroLocationData("ST: Red and White Pinwheel - hill with many pinwheels", "Red and White Pinwheel"),
        SekiroLocationData("ST: Rice for Kuro - Divine Child for Persimmon", "Rice for Kuro", npc=True,
                           conditional=True),
        SekiroLocationData("ST: Scrap Iron - uphill from Kotaro", "Scrap Iron x2"),
        SekiroLocationData("ST: Scrap Magnetite - before Sunken Valley Cavern idol", "Scrap Magnetite",
                           conditional=True),
        SekiroLocationData("ST: Scrap Magnetite - next to Temple Grounds idol", "Scrap Magnetite"),
        SekiroLocationData("ST: Scrap Magnetite - on slope leading to Main Hall, enemy drop", "Scrap Magnetite",
                           drop=True),
        SekiroLocationData("ST: Senpou Esoteric Text - pagoda after Main Hall cave", "Senpou Esoteric Text"),
        SekiroLocationData("ST: Snap Seed - after kite jump", "Snap Seed x2", conditional=True),
        SekiroLocationData("ST: Ungo's Sugar - along slope leading to Main Hall", "Ungo's Sugar"),
        SekiroLocationData("ST: Ungo's Sugar - Main Hall, right wing", "Ungo's Sugar"),
        SekiroLocationData("ST: Ungo's Sugar - right balcony before broken bridge", "Ungo's Sugar"),
        SekiroLocationData("ST: Ungo's Sugar - under stairs before Main Hall", "Ungo's Sugar x3"),
        SekiroLocationData("ST: White Pinwheel - hidden cliff before Bell Demon's Temple idol", "White Pinwheel"),
        SekiroLocationData("ST: Yellow Gunpowder - cliffside temple, miniboss drop", "Yellow Gunpowder x2",
                           missable=True),
    ],
    "Sunken Valley": [
        SekiroLocationData("SV: Antidote Powder - right ledge near buddha head", "Antidote Powder"),
        SekiroLocationData("SV: Antidote Powder - shimmy before Sunken Valley idol", "Antidote Powder"),
        SekiroLocationData("SV: Black Gunpowder - along path to Gun Fort entrance", "Black Gunpowder"),
        SekiroLocationData("SV: Black Gunpowder - right Gun Fort barricade", "Black Gunpowder x2"),
        SekiroLocationData("SV: Ceramic Shard - right ledge before hidden encampment path", "Ceramic Shard"),
        SekiroLocationData("SV: Contact Medicine - fort chasm, bottom ledge", "Contact Medicine"),
        SekiroLocationData("SV: Divine Confetti - fort chasm, dead-end tunnel", "Divine Confetti x3"),
        SekiroLocationData("SV: Divine Grass - pond cave, behind giant pillar", "Divine Grass", conditional=True,
                           hidden=True, diving=True),
        SekiroLocationData("SV: Fistful of Ash - on ground right of buddha head", "Fistful of Ash x2"),
        SekiroLocationData("SV: Fistful of Ash - right of Under-Shrine Valley idol", "Fistful of Ash x2"),
        SekiroLocationData("SV: Gokan's Spiritfall - pond cave, miniboss drop", "Gokan's Spiritfall", conditional=True,
                           headless=True, diving=True),
        SekiroLocationData("SV: Gokan's Sugar - ledge left of fort entrance", "Gokan's Sugar", hidden=True),
        SekiroLocationData("SV: Gourd Seed - behind hidden encampment", "Gourd Seed"),
        SekiroLocationData("SV: Heavy Coin Purse - Gun Fort, under wooden battlement", "Heavy Coin Purse"),
        SekiroLocationData("SV: Large Fan - Gun Fort shrine, statue", "Large Fan"),
        SekiroLocationData("SV: Lump of Grave Wax - pond cave, behind miniboss", "Lump of Grave Wax", conditional=True,
                           diving=True),
        SekiroLocationData("SV: Mibu Balloon of Soul - fort chasm, wooden planks", "Mibu Balloon of Soul x3"),
        SekiroLocationData("SV: Pacifying Agent - before pond cave, behind frozen waterfall", "Pacifying Agent x3",
                           hidden=True),
        SekiroLocationData("SV: Pacifying Agent - before pond cave, near pond", "Pacifying Agent"),
        SekiroLocationData("SV: Pellet - Gun Fort, under wooden battlement", "Pellet x2"),
        SekiroLocationData("SV: Prayer Bead - before Gun Fort, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("SV: Prayer Bead - fort chasm, bottom ledge", "Prayer Bead"),
        SekiroLocationData("SV: Prayer Bead - Gun Fort shrine, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("SV: Prayer Bead - on ground before pond cave", "Prayer Bead"),
        SekiroLocationData("SV: Scrap Magnetite - Gun Fort shrine, right of statue", "Scrap Magnetite"),
        SekiroLocationData("SV: Scrap Magnetite - ledge behind Gun Fort barricades", "Scrap Magnetite"),
        SekiroLocationData("SV: Scrap Magnetite - right of Sunken Valley idol", "Scrap Magnetite"),
        SekiroLocationData("SV: Scrap Magnetite - rightmost ledge overlooking rope bridge", "Scrap Magnetite"),
        SekiroLocationData("SV: Scrap Magnetite - slope left of buddha head", "Scrap Magnetite"),
        SekiroLocationData("SV: Snap Seed - Gun Fort, on wooden battlement", "Snap Seed x3"),
        SekiroLocationData("SV: Ungo's Sugar - atop stone pillar facing Fort entrance", "Ungo's Sugar", hidden=True),
        SekiroLocationData("SV: Yellow Gunpowder - floor before Gun Fort idol, enemy drop", "Yellow Gunpowder x3",
                           drop=True),
        SekiroLocationData("SV: Yellow Gunpowder - Gun Fort shrine, below in crawl space", "Yellow Gunpowder"),
        SekiroLocationData("SV: Yellow Gunpowder - Gun Fort shrine, miniboss drop", "Yellow Gunpowder x2",
                           missable=True),
        SekiroLocationData("SV: Yellow Gunpowder - Gun Fort, under wooden battlement", "Yellow Gunpowder"),
        SekiroLocationData("SV: Yellow Gunpowder - hidden encampment", "Yellow Gunpowder"),
    ],
    "Sunken Valley Passage": [
        SekiroLocationData("SVP: Adamantite Scrap - grapple spot above Riven Cave idol", "Adamantite Scrap"),
        SekiroLocationData("SVP: Adamantite Scrap - underwater, opposite from Riven Cave in lake", "Adamantite Scrap",
                           conditional=True, diving=True),
        SekiroLocationData("SVP: Ako's Sugar - base of third left bodhi statue", "Ako's Sugar x2"),
        SekiroLocationData("SVP: Antidote Powder -  shrine cave, shortly after entering", "Antidote Powder x2"),
        SekiroLocationData("SVP: Bulging Coin Purse - underwater, next to log in middle of lake", "Bulging Coin Purse",
                           conditional=True, diving=True),
        SekiroLocationData("SVP: Bundled Jizo Statue - Sunken Valley Cavern, after killing serpent",
                           "Bundled Jizo Statue",
                           missable=True, conditional=True),
        SekiroLocationData("SVP: Contact Medicine - behind last upright left bodhi statue", "Contact Medicine x3"),
        SekiroLocationData("SVP: Contact Medicine - dropdown after broken bodhi head", "Contact Medicine x3"),
        SekiroLocationData("SVP: Divine Confetti - underground shrine, on ledge above", "Divine Confetti x3",
                           conditional=True),
        SekiroLocationData("SVP: Dragon's Blood Droplet - Sunken Valley Cavern, after killing serpent",
                           "Dragon's Blood Droplet", missable=True, conditional=True),
        SekiroLocationData("SVP: Dried Serpent Viscera - underground shrine, statue", "Dried Serpent Viscera",
                           progression=True, conditional=True),
        SekiroLocationData("SVP: Fistful of Ash - shrine cave, group of three items", "Fistful of Ash"),
        SekiroLocationData("SVP: Fistful of Ash - shrine cave, under low arch", "Fistful of Ash x2"),
        SekiroLocationData("SVP: Fresh Serpent Viscera - Sunken Valley Cavern, plunge kill serpent",
                           "Fresh Serpent Viscera", progression=True, drop=True, conditional=True),
        SekiroLocationData("SVP: Fulminated Mercury - swamp island, behind left mound", "Fulminated Mercury"),
        SekiroLocationData("SVP: Gachiin's Sugar - underwater, opposite from Riven Cave in lake", "Gachiin's Sugar x3",
                           conditional=True, diving=True),
        SekiroLocationData("SVP: Great White Whisker - Guardian Ape's Watering Hole, after killing Giant Carp",
                           "Great White Whisker", conditional=True),
        SekiroLocationData("SVP: Green Mossy Gourd - Toxic Memorial Mob", "Green Mossy Gourd", npc=True, shop=True),
        SekiroLocationData("SVP: Heavy Coin Purse - swamp below Bodhisattva Valley idol", "Heavy Coin Purse"),
        SekiroLocationData("SVP: Light Coin Purse - swamp island, behind right mound", "Light Coin Purse"),
        SekiroLocationData("SVP: Lotus of the Palace - cave behind Guardian Ape's Watering Hole idol",
                           "Lotus of the Palace", prominent=True, progression=True),
        SekiroLocationData("SVP: Memory: Guardian Ape - Guardian Ape's Watering Hole, boss drop",
                           "Memory: Guardian Ape",
                           prominent=True, boss=True),
        SekiroLocationData("SVP: Mibu Balloon of Soul - ledge facing swamp island", "Mibu Balloon of Soul"),
        SekiroLocationData("SVP: Mibu Balloon of Soul - ledge under Bodhisattva Valley idol", "Mibu Balloon of Soul"),
        SekiroLocationData("SVP: Mibu Balloon of Soul - Sunken Valley Cavern, lake overlook after killing Serpent",
                           "Mibu Balloon of Soul", missable=True, conditional=True),
        SekiroLocationData("SVP: Mibu Balloon of Soul - underground shrine, back porch", "Mibu Balloon of Soul",
                           conditional=True),
        SekiroLocationData("SVP: Monkey Booze - kill 23-enemy cluster between statues", "Monkey Booze", drop=True),
        SekiroLocationData("SVP: Pacifying Agent - in front of broken bodhi head", "Pacifying Agent"),
        SekiroLocationData("SVP: Pacifying Agent - ledge next to 23-enemy cluster", "Pacifying Agent"),
        SekiroLocationData("SVP: Pellet - shrine cave, group of three items", "Pellet x2"),
        SekiroLocationData("SVP: Precious Bait - underwater, in Guardian Ape's Watering Hole", "Precious Bait",
                           conditional=True, diving=True),
        SekiroLocationData("SVP: Scrap Iron - behind 23-enemy cluster", "Scrap Iron x3"),
        SekiroLocationData("SVP: Scrap Magnetite - behind fallen bodhi statue's head", "Scrap Magnetite"),
        SekiroLocationData("SVP: Scrap Magnetite - shrine cave, group of three items", "Scrap Magnetite"),
        SekiroLocationData("SVP: Scrap Magnetite - shrine cave, late along left wall and up", "Scrap Magnetite x2"),
        SekiroLocationData("SVP: Scrap Magnetite - swamp island, dead tree", "Scrap Magnetite"),
        SekiroLocationData("SVP: Slender Finger - Guardian Ape's Watering Hole, boss drop", "Slender Finger",
                           boss=True),
        SekiroLocationData("SVP: Snap Seed - base of first left bodhi statue", "Snap Seed x3"),
        SekiroLocationData("SVP: Snap Seed - next to Toxic Memorial Mob", "Snap Seed"),
        SekiroLocationData("SVP: Snap Seed - right ledge after Gun Fort shrine", "Snap Seed x2"),
        SekiroLocationData("SVP: Treasure Carp Scale - underwater, in lake before Riven Cave", "Treasure Carp Scale",
                           conditional=True, diving=True),
        SekiroLocationData("SVP: Ungo's Sugar - island before Toxic Memorial Mob", "Ungo's Sugar"),
        SekiroLocationData("SVP: Ungo's Sugar - left side ledge opposite of 23-enemy cluster", "Ungo's Sugar"),
        SekiroLocationData("SVP: Yashariku's Sugar - underwater, in lake between rocks", "Yashariku's Sugar",
                           conditional=True, diving=True),
        SekiroLocationData("SVP: Yellow Gunpowder - before Toxic Memorial Mob, enemy drop", "Yellow Gunpowder",
                           drop=True),
        SekiroLocationData("SVP: Yellow Gunpowder - swamp island, enemy drop", "Yellow Gunpowder", drop=True),
        SekiroLocationData("SVP: Yellow Gunpowder - under Bodhisattva Valley idol in toxic water", "Yellow Gunpowder"),
    ],
    "Poison Pool": [
        SekiroLocationData("PP: Bestowal Ninjutsu - Guardian Ape's Burrow, boss drop", "Bestowal Ninjutsu", boss=True,
                           drop=True, conditional=True),
        SekiroLocationData("PP: Black Gunpowder - left outcropping, among enemies", "Black Gunpowder x2"),
        SekiroLocationData("PP: Heavy Coin Purse - in poison against wall", "Heavy Coin Purse"),
        SekiroLocationData("PP: Malcontent's Ring - Guardian Ape's Burrow, miniboss drop", "Malcontent's Ring",
                           miniboss=True, conditional=True),
        SekiroLocationData("PP: Memory: Headless Ape - Guardian Ape's Burrow, boss drop", "Memory: Headless Ape",
                           prominent=True, boss=True, conditional=True),
        SekiroLocationData("PP: Mibu Possession Balloon - central island", "Mibu Possession Balloon x3"),
        SekiroLocationData("PP: Monkey Booze - above Guardian Ape's Burrow", "Monkey Booze"),
        SekiroLocationData("PP: Oil - ledge above Poison Pool idol", "Oil x3"),
        SekiroLocationData("PP: Pacifying Agent - next to Ashina Depths idol", "Pacifying Agent x2"),
        SekiroLocationData("PP: Pellet - tiny island next to Poison Pool idol", "Pellet x2"),
        SekiroLocationData("PP: Prayer Bead - Guardian Ape's Burrow, boss drop", "Prayer Bead", static='06,0:6798::',
                           boss=True, conditional=True),
        SekiroLocationData("PP: Prayer Bead - Guardian Ape's Burrow, boss drop", "Prayer Bead", static='06,0:6799::',
                           boss=True, conditional=True),
        SekiroLocationData("PP: Prayer Bead - Poison Pool, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("PP: Prayer Bead - top of tallest statue", "Prayer Bead", hidden=True),
        SekiroLocationData("PP: Scrap Magnetite - central island", "Scrap Magnetite"),
        SekiroLocationData("PP: Scrap Magnetite - hand of giant statue against wall", "Scrap Magnetite"),
        SekiroLocationData("PP: Scrap Magnetite - left outcropping, among enemies", "Scrap Magnetite"),
        SekiroLocationData("PP: Yellow Gunpowder - behind stone head near left wall", "Yellow Gunpowder"),
        SekiroLocationData("PP: Yellow Gunpowder - just before tallest statue top", "Yellow Gunpowder"),
    ],
    "Hidden Forest": [
        SekiroLocationData("HF: Adamantite Scrap - on ledge opposite of temple", "Adamantite Scrap"),
        SekiroLocationData("HF: Bite Down - 3-item group in front of temple", "Bite Down"),
        SekiroLocationData("HF: Bite Down - temple front, right side", "Bite Down"),
        SekiroLocationData("HF: Ceramic Shard - above sinkhole, branch before bonfire", "Ceramic Shard x2"),
        SekiroLocationData("HF: Ceramic Shard - behind temple", "Ceramic Shard x2"),
        SekiroLocationData("HF: Contact Medicine - 3-item group in front of temple", "Contact Medicine x2"),
        SekiroLocationData("HF: Fistful of Ash - cliffside, bonfire near miniboss", "Fistful of Ash"),
        SekiroLocationData("HF: Gachiin's Spiritfall - sinkhole, miniboss drop", "Gachiin's Spiritfall", headless=True),
        SekiroLocationData("HF: Heavy Coin Purse - pit in front of temple", "Heavy Coin Purse"),
        SekiroLocationData("HF: Light Coin Purse - 3-item group in front of temple", "Light Coin Purse"),
        SekiroLocationData("HF: Light Coin Purse - above sinkhole, right side cliff", "Light Coin Purse"),
        SekiroLocationData("HF: Lump of Fat Wax - just after cliffside path", "Lump of Fat Wax"),
        SekiroLocationData("HF: Lump of Fat Wax - sinkhole, next to miniboss", "Lump of Fat Wax"),
        SekiroLocationData("HF: Lump of Grave Wax - temple, miniboss drop", "Lump of Grave Wax", miniboss=True,
                           drop=True),
        SekiroLocationData("HF: Mibu Balloon of Soul - above sinkhole, before second branch", "Mibu Balloon of Soul"),
        SekiroLocationData("HF: Mibu Balloon of Wealth - sinkhole, 3-item group", "Mibu Balloon of Wealth x3"),
        SekiroLocationData("HF: Oil - left of temple", "Oil"),
        SekiroLocationData("HF: Oil - temple, front near stone lantern", "Oil"),
        SekiroLocationData("HF: Pellet - cliffside, ledge hang at end", "Pellet x3"),
        SekiroLocationData("HF: Pellet - sinkhole, 3-item group", "Pellet"),
        SekiroLocationData("HF: Pellet - sinkhole, ledge above Bonfire", "Pellet"),
        SekiroLocationData("HF: Prayer Bead - cliffside, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("HF: Scrap Iron - sinkhole, 3-item group", "Scrap Iron x5"),
        SekiroLocationData("HF: Scrap Magnetite - sinkhole, beside miniboss", "Scrap Magnetite"),
        SekiroLocationData("HF: Scrap Magnetite - sinkhole, gravestone on hill", "Scrap Magnetite"),
        SekiroLocationData("HF: Snap Seed - near shimmy in front of temple", "Snap Seed x3"),
        SekiroLocationData("HF: Unrefined Sake - cliffside, miniboss drop", "Unrefined Sake", missable=True),
        SekiroLocationData("HF: Yashariku's Sugar - inside temple", "Yashariku's Sugar"),
        SekiroLocationData("HF: Yashariku's Sugar - sinkhole, up ledge behind miniboss", "Yashariku's Sugar x3"),
        SekiroLocationData("HF: Yellow Gunpowder - right of temple front, against wall", "Yellow Gunpowder"),
    ],
    "Mibu Village": [
        SekiroLocationData("MV: Adamantite Scrap - behind Head Priest's house", "Adamantite Scrap"),
        SekiroLocationData("MV: Adamantite Scrap - on Inuhiko's house, in bird's nest", "Adamantite Scrap"),
        SekiroLocationData("MV: Adamantite Scrap - right of field with the villagers working", "Adamantite Scrap"),
        SekiroLocationData("MV: Ashina Sake - up the fields, near shrine", "Ashina Sake"),
        SekiroLocationData("MV: Black Gunpowder - on main path before big tree", "Black Gunpowder x2"),
        SekiroLocationData("MV: Breath of Life: Shadow - miniboss drop", "Breath of Life: Shadow", miniboss=True),
        SekiroLocationData("MV: Contact Medicine - at house before Inuhiko's house", "Contact Medicine"),
        SekiroLocationData("MV: Contact Medicine - middle of the field with villagers working", "Contact Medicine x2"),
        SekiroLocationData("MV: Divine Confetti - in building before Water Mill idol", "Divine Confetti"),
        SekiroLocationData("MV: Divine Confetti - statue in Head Priest's house", "Divine Confetti x5"),
        SekiroLocationData("MV: Divine Grass - bottom waterfall chest", "Divine Grass"),
        SekiroLocationData("MV: Dragonspring Sake - Exiled Memorial Mob", "Dragonspring Sake", npc=True, shop=True),
        SekiroLocationData("MV: Dragonspring Sake - Head Priest for Water of the Palace", "Dragonspring Sake", npc=True,
                           conditional=True),
        SekiroLocationData("MV: Fistful of Ash - in front of Inuhiko's house", "Fistful of Ash x3"),
        SekiroLocationData("MV: Fistful of Ash - in second house with hole in roof", "Fistful of Ash x5"),
        SekiroLocationData("MV: Gourd Seed - at big tree bed", "Gourd Seed"),
        SekiroLocationData("MV: Heavy Coin Purse - bird's nest on Head Priest's house", "Heavy Coin Purse"),
        SekiroLocationData("MV: Jinza's Jizo Statue - Jinzaemon reward after killing miniboss", "Jinza's Jizo Statue",
                           missable=True, npc=True, conditional=True),
        SekiroLocationData("MV: Light Coin Purse - bird's nest across river from Head Priest's house",
                           "Light Coin Purse"),
        SekiroLocationData("MV: Light Coin Purse - right of Exiled Memorial Mob, up ledge past enemies",
                           "Light Coin Purse"),
        SekiroLocationData("MV: Light Coin Purse - underwater, pond village side", "Light Coin Purse",
                           static='05,0:51500330::', conditional=True, diving=True),
        SekiroLocationData("MV: Light Coin Purse - underwater, pond village side", "Light Coin Purse",
                           static='05,0:51500340::', conditional=True, diving=True),
        SekiroLocationData("MV: Lump of Fat Wax - behind house closest to Exiled Memorial Mob", "Lump of Fat Wax"),
        SekiroLocationData("MV: Lump of Fat Wax - right before crossing bridge to Head Priest's house",
                           "Lump of Fat Wax"),
        SekiroLocationData("MV: Memory: Corrupted Monk - Wedding Cave, boss drop", "Memory: Corrupted Monk", boss=True),
        SekiroLocationData("MV: Mibu Balloon of Soul - found at the tree bed", "Mibu Balloon of Soul"),
        SekiroLocationData("MV: Mibu Balloon of Soul - grapple from Inuhiko's house, up the path",
                           "Mibu Balloon of Soul x2", hidden=True),
        SekiroLocationData("MV: Mibu Balloon of Soul - left side of pond before docks", "Mibu Balloon of Soul"),
        SekiroLocationData("MV: Mibu Balloon of Soul - on main path behind barricade at shrine",
                           "Mibu Balloon of Soul x2"),
        SekiroLocationData("MV: Mibu Balloon of Wealth - boat by the docks", "Mibu Balloon of Wealth x2"),
        SekiroLocationData("MV: Mibu Breathing Technique - Wedding Cave, boss drop", "Mibu Breathing Technique",
                           prominent=True, progression=True, boss=True),
        SekiroLocationData("MV: Mottled Purple Gourd - Exiled Memorial Mob", "Mottled Purple Gourd", npc=True,
                           shop=True),
        SekiroLocationData("MV: Pacifying Agent - on main path behind Shosuke's house", "Pacifying Agent"),
        SekiroLocationData("MV: Pellet - across pond in boat", "Pellet"),
        SekiroLocationData("MV: Pellet - before descending to MV", "Pellet x2"),
        SekiroLocationData("MV: Pellet - in dried riverbank left of big tree", "Pellet x3"),
        SekiroLocationData("MV: Pellet - top of plank before Water Mill idol", "Pellet x2"),
        SekiroLocationData("MV: Pine Resin Ember - on Inuhiko's house", "Pine Resin Ember"),
        SekiroLocationData("MV: Prayer Bead - miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("MV: Prayer Bead - second floor in Head Priest's house", "Prayer Bead"),
        SekiroLocationData("MV: Prayer Bead - underwater, pond chest", "Prayer Bead", conditional=True, diving=True),
        SekiroLocationData("MV: Precious Bait - underwater, river upstream from Head Priest's house", "Precious Bait",
                           conditional=True, diving=True),
        SekiroLocationData("MV: Red Lump - behind pots in Head Priest's house", "Red Lump x2"),
        SekiroLocationData("MV: Red Carp Eyes - underwater, near the end of the pond, Carp drop", "Red Carp Eyes",
                           drop=True, conditional=True, diving=True),
        SekiroLocationData("MV: Scrap Magnetite - downstream from Mibu Village idol, enemy drop", "Scrap Magnetite",
                           drop=True),
        SekiroLocationData("MV: Shelter Stone - Wedding Cave", "Shelter Stone", prominent=True, progression=True,
                           conditional=True),
        SekiroLocationData("MV: Treasure Carp Scale - Head Priest after Water of the Palace, reload, kill",
                           "Treasure Carp Scale x5", conditional=True),
        SekiroLocationData("MV: Treasure Carp Scale - near enemy downstream from Mibu Village idol",
                           "Treasure Carp Scale"),
        SekiroLocationData("MV: Yellow Gunpowder - in building before Water Mill idol", "Yellow Gunpowder"),
    ],
    "Ashina Castle - Interior Ministry": [
        SekiroLocationData("AC2: Adamantite Scrap - Ashina Dojo idol room", "Adamantite Scrap"),
        SekiroLocationData("AC2: Adamantite Scrap - basement, central structure", "Adamantite Scrap"),
        SekiroLocationData("AC2: Adamantite Scrap - basement, passage to main stairway", "Adamantite Scrap"),
        SekiroLocationData("AC2: Antidote Powder - secluded courtyard", "Antidote Powder"),
        SekiroLocationData("AC2: Aromatic Branch - Upper Tower roof, boss drop", "Aromatic Branch", prominent=True,
                           progression=True, boss=True),
        SekiroLocationData("AC2: Black Gunpowder - courtyard with lone dead tree", "Black Gunpowder x3"),
        SekiroLocationData("AC2: Black Scroll - balcony of Isshin's watchtower", "Black Scroll"),
        SekiroLocationData("AC2: Ceramic Shard - on bridge to Great Serpent Shrine", "Ceramic Shard"),
        SekiroLocationData("AC2: Divine Grass - Kuro after entering Fountainhead Place", "Divine Grass", missable=True,
                           npc=True, conditional=True),
        SekiroLocationData("AC2: Dragon's Blood Droplet - on a corpse at Serpent Shrine idol",
                           "Dragon's Blood Droplet"),
        SekiroLocationData("AC2: Father's Bell Charm - Emma after eavesdropping on her", "Father's Bell Charm",
                           progression=True, conditional=True),
        SekiroLocationData("AC2: Heavy Coin Purse - near broken bridge to AO, enemy drop", "Heavy Coin Purse",
                           drop=True),
        SekiroLocationData("AC2: Lump of Fat Wax - Ashina Dojo, miniboss drop", "Lump of Fat Wax x2", missable=True),
        SekiroLocationData("AC2: Memory: Great Shinobi - Upper Tower roof, boss drop", "Memory: Great Shinobi",
                           boss=True),
        #SekiroLocationData("AC2: Memory: Isshin Ashina - Upper Tower roof, Shura boss drop", "Memory: Isshin Ashina",
                          #missable=True, conditional=True),
        SekiroLocationData("AC2: Oil - basement, passage to main stairway", "Oil x5"),
        SekiroLocationData("AC2: Oil - courtyard with lone dead tree", "Oil x2"),
        SekiroLocationData("AC2: Oil - main stairway", "Oil x2"),
        #SekiroLocationData("AC2: One Mind - Upper Tower roof, Shura boss drop", "One Mind", missable=True, boss=True,
                           #conditional=True),
        SekiroLocationData("AC2: Pellet - at end of bridge from ADG", "Pellet x2"),
        SekiroLocationData("AC2: Pellet - on a balcony at Isshin's watchtower", "Pellet"),
        SekiroLocationData("AC2: Pellet - on a corpse on rooftop path, overlooking Gyoubu arena", "Pellet x2"),
        SekiroLocationData("AC2: Pellet - Upper Tower, rafters", "Pellet x3"),
        SekiroLocationData("AC2: Prayer Bead - Ashina Dojo, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("AC2: Prayer Bead - basement, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("AC2: Prayer Bead - Great Serpent Shrine, miniboss drop", "Prayer Bead", miniboss=True,
                           offering_box=True),
        SekiroLocationData("AC2: Scrap Magnitite - on a corpse before central tower", "Scrap Magnetite x2"),
        SekiroLocationData("AC2: Shinobi Medicine Rank 3 - basement, miniboss drop", "Shinobi Medicine Rank 3",
                           miniboss=True),
        SekiroLocationData("AC2: Sweet Rice Ball - finish incense and give Rice to Kuro", "Sweet Rice Ball",
                           missable=True, npc=True, conditional=True),
        SekiroLocationData("AC2: Tomoe's Note - Emma after eavesdropping on Kuro", "Tomoe's Note", npc=True),
        SekiroLocationData("AC2: Yashariku's Sugar - moat below Ashina Castle idol", "Yashariku's Sugar"),
        SekiroLocationData("AC2: Yashariku's Sugar - under gate separating Ashina Castle and Serpent Shrine",
                           "Yashariku's Sugar"),
        SekiroLocationData("AC2: Yellow Gunpowder - Great Serpent Shrine, miniboss drop", "Yellow Gunpowder x2",
                           missable=True),
    ],
    "Hirata Estate - Father's Bell Charm": [
        SekiroLocationData("HE2: Adamantite Scrap - burning courtyard, miniboss drop", "Adamantite Scrap x2",
                           missable=True),
        SekiroLocationData("HE2: Adamantite Scrap - Main Hall, on the roof near three enemies", "Adamantite Scrap"),
        SekiroLocationData("HE2: Adamantite Scrap - Main Hall, tree at entrance to Audience Chamber",
                           "Adamantite Scrap"),
        SekiroLocationData("HE2: Aromatic Flower - Hidden Temple, boss drop", "Aromatic Flower", prominent=True,
                           boss=True),
        SekiroLocationData("HE2: Ashina Sake - Main Hall, left building after marsh", "Ashina Sake"),
        SekiroLocationData("HE2: Fistful of Ash - Main Hall, corpse of Ashina Elite near miniboss", "Fistful of Ash"),
        SekiroLocationData("HE2: Fulminated Mercury - after courtyard miniboss", "Fulminated Mercury"),
        SekiroLocationData("HE2: Fulminated Mercury - Audience Chamber, hallway to shinobi door", "Fulminated Mercury"),
        SekiroLocationData("HE2: Gokan's Sugar - Audience Chamber, left second room in left corner",
                           "Gokan's Sugar x2"),
        SekiroLocationData("HE2: Light Coin Purse - Main Hall, left building after marsh", "Light Coin Purse"),
        SekiroLocationData("HE2: Memory: Foster Father - Hidden Temple, boss drop", "Memory: Foster Father", boss=True),
        SekiroLocationData("HE2: Mibu Balloon of Wealth - Main Hall, open area before marsh",
                           "Mibu Balloon of Wealth x2"),
        SekiroLocationData("HE2: Pellet - Audience Chamber, room straight from entrance", "Pellet x3"),
        SekiroLocationData("HE2: Prayer Bead - burning courtyard, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("HE2: Prayer Bead - entrance to Audience Chamber, miniboss drop", "Prayer Bead",
                           miniboss=True),
    ],
    "Fountainhead Palace": [
        SekiroLocationData("FP: A Beast's Karma - beside Mibu Manor, miniboss drop", "A Beast's Karma", miniboss=True),
        SekiroLocationData("FP: Adamantite Scrap - alcove behind first miniboss", "Adamantite Scrap"),
        SekiroLocationData("FP: Adamantite Scrap - courtyard, inside left building", "Adamantite Scrap"),
        SekiroLocationData("FP: Adamantite Scrap - inside building in middle of lake", "Adamantite Scrap"),
        SekiroLocationData("FP: Adamantite Scrap - Mibu Manor, in room with chest", "Adamantite Scrap"),
        SekiroLocationData("FP: Adamantite Scrap - roof of submerged building near Mibu Manor", "Adamantite Scrap"),
        SekiroLocationData("FP: Adamantite Scrap - underwater, further bottom of Great Carp ravine", "Adamantite Scrap",
                           conditional=True, diving=True),
        SekiroLocationData("FP: Ako's Sugar - Feeding Grounds, behind building in back corner", "Ako's Sugar x2",
                           conditional=True, hidden=True, diving=True),
        SekiroLocationData("FP: Ako's Sugar - Mibu Manor, tree outside window at first enemy", "Ako's Sugar x3"),
        SekiroLocationData("FP: Bite Down - Mibu Manor, room with old woman", "Bite Down x2"),
        SekiroLocationData("FP: Bulging Coin Purse - alcove behind first miniboss", "Bulging Coin Purse"),
        SekiroLocationData("FP: Bulging Coin Purse - lower branch near Great Sakura miniboss", "Bulging Coin Purse"),
        SekiroLocationData("FP: Bundled Jizo Statue - behind waterfall miniboss", "Bundled Jizo Statue"),
        SekiroLocationData("FP: Ceramic Shard - bird's nest on wall before courtyard", "Ceramic Shard x3"),
        SekiroLocationData("FP: Ceramic Shard - past bridge, below platforms at water intersection",
                           "Ceramic Shard x3"),
        SekiroLocationData("FP: Ceramic Shard - underwater, entrance to Great Carp ravine", "Ceramic Shard x2",
                           conditional=True, diving=True),
        SekiroLocationData("FP: Divine Confetti - behind pagoda at Flower Viewing Stage idol", "Divine Confetti x3"),
        SekiroLocationData("FP: Divine Confetti - Mibu Manor, far left corner", "Divine Confetti x2"),
        SekiroLocationData("FP: Divine Confetti - near Pot Noble Koremori", "Divine Confetti x2"),
        SekiroLocationData("FP: Divine Dragon's Tears - Sanctuary, boss drop", "Divine Dragon's Tears", prominent=True,
                           progression=True, boss=True, conditional=True, diving=True),
        SekiroLocationData("FP: Divine Grass - Feeding Attendant for Great White Whisker", "Divine Grass",
                           missable=True, npc=True, conditional=True, diving=True),
        SekiroLocationData("FP: Divine Grass - Mibu Manor, chest in room across water", "Divine Grass"),
        SekiroLocationData("FP: Dragon's Blood Droplet - left of Sanctuary idol", "Dragon's Blood Droplet",
                           conditional=True, diving=True),
        SekiroLocationData("FP: Dragon's Blood Droplet - Pot Noble Koremori", "Dragon's Blood Droplet", npc=True,
                           shop=True),
        SekiroLocationData("FP: Dragon's Tally Board - Vermilion Bridge, boss drop", "Dragon's Tally Board",
                           prominent=True, boss=True),
        SekiroLocationData("FP: Dragonspring Sake - before Great Sakura idol, enemy drop", "Dragonspring Sake",
                           drop=True),
        SekiroLocationData("FP: Eel Liver - courtyard, behind bridge", "Eel Liver x2"),
        SekiroLocationData("FP: Eel Liver - Mibu Manor, first house on left", "Eel Liver x3"),
        SekiroLocationData("FP: Eel Liver - past bridge, end of small stream left", "Eel Liver x2"),
        SekiroLocationData("FP: Gokan's Sugar - past bridge, left-most high roof", "Gokan's Sugar x3"),
        SekiroLocationData("FP: Gourd Seed - Palace Grounds, chest", "Gourd Seed", conditional=True, diving=True),
        SekiroLocationData("FP: Heavy Coin Purse - courtyard, middle between trees", "Heavy Coin Purse"),
        SekiroLocationData("FP: Heavy Coin Purse - Feeding Grounds, bridge", "Heavy Coin Purse", conditional=True,
                           diving=True),
        SekiroLocationData("FP: Heavy Coin Purse - past bridge, giant tree base, left", "Heavy Coin Purse"),
        SekiroLocationData("FP: Lapis Lazuli - Koremori's pot after Truly Precious Bait", "Lapis Lazuli", missable=True,
                           conditional=True, diving=True),
        SekiroLocationData("FP: Lapis Lazuli - past bridge, at waterfall, miniboss drop", "Lapis Lazuli",
                           miniboss=True),
        SekiroLocationData("FP: Light Coin Purse - log left of first building", "Light Coin Purse"),
        SekiroLocationData("FP: Light Coin Purse - past bridge, giant tree base, front", "Light Coin Purse"),
        SekiroLocationData("FP: Light Coin Purse - underwater, building overlooking headless", "Light Coin Purse",
                           conditional=True, diving=True),
        SekiroLocationData("FP: Light Coin Purse - underwater, near bottom of Great Carp ravine", "Light Coin Purse",
                           conditional=True, diving=True),
        SekiroLocationData("FP: Light Coin Purse - underwater, plants near Pot Noble Koremori", "Light Coin Purse",
                           conditional=True, diving=True),
        SekiroLocationData("FP: Lump of Grave Wax - barely-above water roof in lake", "Lump of Grave Wax"),
        SekiroLocationData("FP: Lump of Grave Wax - first bridge into water", "Lump of Grave Wax"),
        SekiroLocationData("FP: Lump of Grave Wax - Mibu Manor, booth in house with rafters", "Lump of Grave Wax"),
        SekiroLocationData("FP: Lump of Grave Wax - underwater, building with Old Woman on roof", "Lump of Grave Wax",
                           conditional=True, diving=True),
        SekiroLocationData("FP: Mask Fragment: Left - Pot Noble Koremori", "Mask Fragment: Left", npc=True, shop=True),
        SekiroLocationData("FP: Memory: Divine Dragon - Sanctuary, boss drop", "Memory: Divine Dragon", boss=True,
                           conditional=True, diving=True),
        SekiroLocationData("FP: Memory: True Monk - Vermilion Bridge, boss drop", "Memory: True Monk", boss=True),
        SekiroLocationData("FP: Mibu Balloon of Soul - first building after descent from first boss",
                           "Mibu Balloon of Soul"),
        SekiroLocationData("FP: Mibu Balloon of Soul - Palace Grounds, pool of water", "Mibu Balloon of Soul x3",
                           conditional=True, diving=True),
        SekiroLocationData("FP: Mibu Balloon of Soul - past bridge, building across from bridge",
                           "Mibu Balloon of Soul"),
        SekiroLocationData("FP: Mibu Balloon of Soul - past bridge, underneath first platform", "Mibu Balloon of Soul"),
        SekiroLocationData("FP: Mibu Balloon of Wealth - second building backside, room under overhang ",
                           "Mibu Balloon of Wealth"),
        SekiroLocationData("FP: Mibu Possession Balloon - by three enemies near waterfall miniboss",
                           "Mibu Possession Balloon", static='08,0:52500330::'),
        SekiroLocationData("FP: Mibu Possession Balloon - by three enemies near waterfall miniboss",
                           "Mibu Possession Balloon", static='08,0:52500340::'),
        SekiroLocationData("FP: Pellet - along the wall at first miniboss", "Pellet x2"),
        SekiroLocationData("FP: Pellet - beginning of area behind collapsed strawman", "Pellet x2"),
        SekiroLocationData("FP: Pellet - Mibu Manor, central open area under tree", "Pellet"),
        SekiroLocationData("FP: Pellet - past bridge, left before stairs to Palace Grounds", "Pellet x2"),
        SekiroLocationData("FP: Prayer Bead - Great Sakura, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("FP: Prayer Bead - outside Mibu Manor, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("FP: Prayer Bead - underwater, chest near giant fish skeleton", "Prayer Bead",
                           conditional=True, diving=True),
        SekiroLocationData("FP: Precious Bait - underwater, below Feeding Grounds", "Precious Bait", conditional=True,
                           diving=True),
        SekiroLocationData("FP: Precious Bait - underwater, building beneath Great Sakura miniboss", "Precious Bait",
                           conditional=True, diving=True),
        SekiroLocationData("FP: Precious Bait - underwater, log near headless", "Precious Bait", conditional=True,
                           diving=True),
        SekiroLocationData("FP: Red Lump - underwater, right of demolished bridge", "Red Lump", conditional=True,
                           diving=True),
        SekiroLocationData("FP: Scrap Magnetite - underwater, plants near Pot Noble Koremori", "Scrap Magnetite x3",
                           conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - feed Great Carp once", "Treasure Carp Scale x3", npc=True,
                           conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - feed Great Carp twice", "Treasure Carp Scale", npc=True,
                           conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - Mibu Manor, dive in left corner before exit",
                           "Treasure Carp Scale", static='08,0:52500100::', conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - Mibu Manor, dive in left corner before exit",
                           "Treasure Carp Scale", static='08,0:52500120::', conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - Mibu Manor, dive in left corner before exit",
                           "Treasure Carp Scale", static='08,0:52500570::', conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - underwater, giant skeleton near headless", "Treasure Carp Scale",
                           static='08,0:52500480::', conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - underwater, giant skeleton near headless", "Treasure Carp Scale",
                           static='08,0:52500490::', conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - underwater, inside house along right wall", "Treasure Carp Scale",
                           static='08,0:52500440::', conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - underwater, inside house along right wall", "Treasure Carp Scale",
                           static='08,0:52500450::', conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - underwater, inside house along right wall", "Treasure Carp Scale",
                           static='08,0:52500460::', conditional=True, diving=True),
        SekiroLocationData("FP: Truly Precious Bait - Pot Noble Koremori after 9 scales", "Truly Precious Bait",
                           missable=True, npc=True),
        SekiroLocationData("FP: Ungo's Sugar - courtyard, middle between trees", "Ungo's Sugar"),
        SekiroLocationData("FP: Ungo's Sugar - Feeding Grounds, up the stairs from idol", "Ungo's Sugar x2",
                           conditional=True, diving=True),
        SekiroLocationData("FP: Water of the Palace - Mibu Manor, dive in left corner before exit, chest",
                           "Water of the Palace", conditional=True, diving=True),
        SekiroLocationData("FP: Yashariku's Spiritfall - underwater, headless drop", "Yashariku's Spiritfall",
                           conditional=True, headless=True, diving=True),
        SekiroLocationData("FP: Yashariku's Sugar - alcove behind first miniboss", "Yashariku's Sugar x3"),
        SekiroLocationData("FP: Yashariku's Sugar - courtyard, tree left of door to idol", "Yashariku's Sugar x2"),
        SekiroLocationData("FP: Yellow Gunpowder - Mibu Manor, first house on left dead end", "Yellow Gunpowder x4"),
    ],
    "Ashina Castle - Central Forces": [
        SekiroLocationData("AC3: Adamantite Scrap - top of main stairway", "Adamantite Scrap x2"),
        SekiroLocationData("AC3: Adamantite Scrap - Upper Tower, map room", "Adamantite Scrap"),
        SekiroLocationData("AC3: Ako's Sugar - area right of main stairway", "Ako's Sugar x3"),
        SekiroLocationData("AC3: Bundled Jizo Statue - along path to Serpent Shrine, enemy drop", "Bundled Jizo Statue",
                           drop=True),
        SekiroLocationData("AC3: Fistful of Ash - courtyard before Old Grave idol", "Fistful of Ash"),
        SekiroLocationData("AC3: Fulminated Mercury - alcove on right at main stairway", "Fulminated Mercury"),
        SekiroLocationData("AC3: Gokan's Sugar - courtyard left of Ashina Castle idol", "Gokan's Sugar x3"),
        SekiroLocationData("AC3: Mibu Pilgrimage Balloon - complete Blackhat Badger quest", "Mibu Pilgrimage Balloon",
                           missable=True, conditional=True),
        SekiroLocationData("AC3: Ministry Dousing Powder - along main stairway", "Ministry Dousing Powder"),
        SekiroLocationData("AC3: Pellet - Upper Tower, room before stairs to Ashina Dojo", "Pellet x3"),
        SekiroLocationData("AC3: Prayer Bead - bottom of Isshin's Tower, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("AC3: Secret Passage Key - Emma", "Secret Passage Key", npc=True, prominent=True,
                           progression=True),
        SekiroLocationData("AC3: Yashariku's Sugar - Isshin's dojo, near miniboss", "Yashariku's Sugar x2"),
    ],
    "Ashina Outskirts - Burning": [
        SekiroLocationData("AO2: Adamantite Scrap - before teleport to Flames of Hatred idol", "Adamantite Scrap"),
        SekiroLocationData("AO2: Adamantite Scrap - headless warning sign", "Adamantite Scrap"),
        SekiroLocationData("AO2: Adamantite Scrap - lookout tower top near Stairway idol", "Adamantite Scrap"),
        SekiroLocationData("AO2: Dragon's Blood Droplet - inside Tengu tower, ground floor", "Dragon's Blood Droplet"),
        SekiroLocationData("AO2: Fistful of Ash - tower base near Stairway idol", "Fistful of Ash x3"),
        SekiroLocationData("AO2: Fulminated Mercury - explosive crates near cannon", "Fulminated Mercury"),
        SekiroLocationData("AO2: Fulminated Mercury - explosive crates near fortress courtyard", "Fulminated Mercury"),
        SekiroLocationData("AO2: Gachiin's Sugar - behind Anayama's first shop", "Gachiin's Sugar x3"),
        SekiroLocationData("AO2: Gachiin's Sugar - lookout building, middle room", "Gachiin's Sugar x2"),
        SekiroLocationData("AO2: Heavy Coin Purse - lookout building, right room", "Heavy Coin Purse"),
        SekiroLocationData("AO2: Lapis Lazuli - Flames of Hatred, boss drop", "Lapis Lazuli x2", boss=True),
        SekiroLocationData("AO2: Lump of Grave Wax - base of tower before cliff courtyard", "Lump of Grave Wax"),
        SekiroLocationData("AO2: Lump of Grave Wax - stairs leading to Tengu tower", "Lump of Grave Wax"),
        SekiroLocationData("AO2: Memory: Hatred Demon - Flames of Hatred, boss drop", "Memory: Hatred Demon",
                           prominent=True, boss=True),
        SekiroLocationData("AO2: Ministry Dousing Powder - after rebuilt bridge outskirts side",
                           "Ministry Dousing Powder x2"),
        SekiroLocationData("AO2: Ministry Dousing Powder - explosive crates after Inosuke's house",
                           "Ministry Dousing Powder x2"),
        SekiroLocationData("AO2: Pellet -  lookout tower base near Stairway idol", "Pellet x2"),
        SekiroLocationData("AO2: Pellet - destroyed house, second floor", "Pellet x3"),
        SekiroLocationData("AO2: Prayer Bead - near Stairway idol, miniboss drop", "Prayer Bead", miniboss=True),
        SekiroLocationData("AO2: Promissory Note - Anayama the Peddler", "Promissory Note", missable=True, npc=True,
                           shop=True, conditional=True),
    ],
    "Ashina Reservoir - Endgame": [
        SekiroLocationData("AR3: Dragon Flash - final boss drop", "Dragon Flash", boss=True, conditional=True),
        SekiroLocationData("AR3: Fulminated Mercury - behind miniboss against gate", "Fulminated Mercury"),
        SekiroLocationData("AR3: Memory: Saint Isshin - final boss drop", "Memory: Saint Isshin", boss=True,
                           conditional=True),
        SekiroLocationData("AR3: Ministry Dousing Powder - tree near miniboss", "Ministry Dousing Powder x2"),
        SekiroLocationData("AR3: Pellet - under bridge before Secret Passage", "Pellet x3"),
        SekiroLocationData("AR3: Prayer Bead - miniboss drop", "Prayer Bead", miniboss=True),
    ],
}
# Add Carp drops in case of Carpsanity being active
if SekiroOptions.carpsanity:
    location_tables["Hirata Estate - Young Lord's Bell Charm"].extend([
        SekiroLocationData("HE1: Treasure Carp Scale - near bridge, Carp drop", "Treasure Carp Scale", drop=True),
        SekiroLocationData("HE1: Treasure Carp Scale - near Pot Noble Harunaga, Carp drop", "Treasure Carp Scale",
                           drop=True),
        SekiroLocationData("HE1: Treasure Carp Scale - under Bamboo Thicket Slope bridge, Carp drop",
                           "Treasure Carp Scale", drop=True),
        SekiroLocationData("HE1: Treasure Carp Scale - underwater, in Dragonspring Lake, Carp drop",
                           "Treasure Carp Scale", static='03,0:52500964::', drop=True, conditional=True, diving=True),
        SekiroLocationData("HE1: Treasure Carp Scale - underwater, in Dragonspring Lake, Carp drop",
                           "Treasure Carp Scale", static='03,0:52500965::', drop=True, conditional=True, diving=True),
        SekiroLocationData("HE1: Treasure Carp Scale - underwater, under Bamboo Thicket Slope bridge, Carp drop",
                           "Treasure Carp Scale", drop=True, conditional=True, diving=True),
    ])
    location_tables["Ashina Castle"].append(
        SekiroLocationData("AC1: Treasure Carp Scale - underwater, below Ashina Castle idol, Carp drop",
                           "Treasure Carp Scale", drop=True, conditional=True, diving=True),
    )
    location_tables["Senpou Temple, Mt. Kongo"].extend([
        SekiroLocationData("ST: Treasure Carp Scale - pond, Carp drop", "Treasure Carp Scale", static='07,0:52500970::',
                           drop=True),
        SekiroLocationData("ST: Treasure Carp Scale - pond, Carp drop", "Treasure Carp Scale", static='07,0:52500971::',
                           drop=True),
    ])
    location_tables["Sunken Valley Passage"].extend([
        SekiroLocationData("SVP: Treasure Carp Scale - close to Riven Cave entrance, Carp drop", "Treasure Carp Scale",
                           drop=True),
        SekiroLocationData("SVP: Treasure Carp Scale - underwater, far from Riven Cave entrance, Carp drop",
                           "Treasure Carp Scale", drop=True, conditional=True, diving=True),
    ])
    location_tables["Mibu Village"].append(
        SekiroLocationData("MV: Treasure Carp Scale - underwater, near Water Mill idol, Carp drop",
                           "Treasure Carp Scale", drop=True, conditional=True, diving=True),
    )
    location_tables["Fountainhead Palace"].extend([
        SekiroLocationData("FP: Treasure Carp Scale - underwater, beneath Feeding Grounds, Carp drop",
                           "Treasure Carp Scale", drop=True, conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - underwater, further out from first bridge, Carp drop",
                           "Treasure Carp Scale", drop=True, conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - underwater, middle of the lake, Carp drop", "Treasure Carp Scale",
                           drop=True, conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - underwater, near first bridge, Carp drop", "Treasure Carp Scale",
                           drop=True, conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - underwater, near first house of area, Carp drop",
                           "Treasure Carp Scale", drop=True, conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - underwater, right wall before building, Carp drop",
                           "Treasure Carp Scale", drop=True, conditional=True, diving=True),
        SekiroLocationData("FP: Treasure Carp Scale - underwater, under Sakura Branch, Carp drop",
                           "Treasure Carp Scale", drop=True, conditional=True, diving=True),
    ])


for i, region in enumerate(region_order):
    for location in location_tables[region]: location.region_value = i

location_name_groups: Dict[str, Set[str]] = {
    # We could insert these locations automatically with setdefault(), but we set them up explicitly
    # instead so we can choose the ordering.
    "Prominent": set(),
    "Progression": set(),
    "Boss Rewards": set(),
    "Miniboss Rewards": set(),
    "Hostile": set(),
    "Friendly": set(),
    "Esoteric Texts": set(),
    "Skills": set(),
    "Upgrade": set(),
    "Currency": set(),
    "Memories": set(),
    "Unique": set(),
    "Healing": set(),
    "Miscellaneous": set(),
    "Hidden": set(),
    "Offering Box": set(),
}

location_descriptions = {
    "Prominent": "A small number of locations that are in very obvious locations. Mostly boss " + \
                 "drops. Ideal for setting as priority locations.",
    "Progression": "Locations that contain items in vanilla which unlock other locations.",
    "Boss Rewards": "Boss drops. Bosses are strong enemies that drop memories.",
    "Miniboss Rewards": "Miniboss drops. Minibosses are enemies with unique health bars that do not drop memories.",
    "Hostile": "Drops from regular enemies or NPCs that are hostile to you.",
    "Friendly": "Items given by friendly NPCs as part of their quests or from " + \
                "non-violent interaction.",
    "Esoteric Texts": "Locations that contain an esoteric text item",
    "SKills": "Locations that contain skills found as item drops, such as " +
              "Shinobi Medicine or Ninjutsu Techniques.",
    "Upgrade": "Locations that contain non-unique upgrade materials for prosthetic tools.",
    "Currency": "Locations that contain coin pouches and treasure carp scales in vanilla.",
    "Memories": "Locations that contain memories in vanilla.",
    "Unique": "Locations that contain items which can be obtained once in a run, such as keys, notes, " + \
              "reusable items, prosthetics & unique upgrades.",
    "Healing": "Locations that contain Prayer Beads and Gourd Seeds in vanilla.",
    "Miscellaneous": "Locations that contain generic stackable items in vanilla, such as sugars, " +
                     "mibu balloons, sakes, and so on.",
    "Hidden": "Locations that are particularly difficult to find, such as in crawl spaces, " + \
              "down hidden drops, behind walls and so on.",
    "Offering Box": "Locations that contain items which move into the Offering Box after " + \
                    "becoming unavailable elsewhere."
}

location_dictionary: Dict[str, SekiroLocationData] = {}
for location_name, location_table in location_tables.items():
    location_dictionary.update({location_data.name: location_data for location_data in location_table})

for location_data in location_table:
    if not location_data.is_event:
        for group_name in location_data.location_groups():
            location_name_groups[group_name].add(location_data.name)

# Allow entire locations to be added to location sets.
if not location_name.endswith(" Shop"):
    location_name_groups[location_name] = set([
        location_data.name for location_data in location_table
        if not location_data.is_event
    ])
