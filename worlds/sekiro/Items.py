from dataclasses import dataclass
import dataclasses
from enum import IntEnum
from typing import ClassVar, Dict, Generator, List, Optional, Set

from BaseClasses import Item, ItemClassification


class SekiroItemCategory(IntEnum):
    ESOTERIC_TEXTS = 0
    SKILLS = 1
    HEALING = 2
    INCENSE = 3
    MEMORIES = 4
    MISC = 5
    CURRENCY = 6
    UNIQUE = 7
    UPGRADE = 8


@dataclass
class SekiroItemData:
    __item_id: ClassVar[int] = 100000
    """The next item ID to use when creating item data."""

    name: str
    sekiro_code: Optional[int]
    category: SekiroItemCategory

    base_name: Optional[str] = None
    """The name of the individual item, if this is a multi-item group."""

    classification: ItemClassification = ItemClassification.filler
    """How important this item is to the game progression."""

    ap_code: Optional[int] = None
    """The Archipelago ID for this item."""

    count: int = 1
    """The number of copies of this item included in each drop."""

    inject: bool = False
    """If this is set, the randomizer will try to inject this item into the game.

    This is used for items such as covenant rewards that aren't realistically reachable in a
    randomizer run, but are still fun to have available to the player. If there are more locations
    available than there are items in the item pool, these items will be used to help make up the
    difference.
    """

    filler: bool = False
    """Whether this is a candidate for a filler item to be added to fill out extra locations."""

    skip: bool = False
    """Whether to omit this item from randomization and replace it with filler or unique items."""

    @property
    def unique(self):
        """Whether this item should be unique, appearing only once in the randomizer."""
        return self.category not in {
            SekiroItemCategory.MISC, SekiroItemCategory.CURRENCY, SekiroItemCategory.UPGRADE,
            SekiroItemCategory.HEALING,
        }

    def __post_init__(self):
        self.ap_code = self.ap_code or SekiroItemData.__item_id
        if not self.base_name: self.base_name = self.name
        SekiroItemData.__item_id += 1

    def item_groups(self) -> List[str]:
        """The names of item groups this item should appear in.

        This is computed from the properties assigned to this item."""
        names = []
        if self.classification == ItemClassification.progression: names.append("Progression")

        names.append({
                         SekiroItemCategory.ESOTERIC_TEXTS: "Esoteric Texts",
                         SekiroItemCategory.SKILLS: "Skills",
                         SekiroItemCategory.MISC: "Miscellaneous",
                         SekiroItemCategory.INCENSE: "Incense",
                         SekiroItemCategory.UNIQUE: "Unique",
                         SekiroItemCategory.MEMORIES: "Memories",
                         SekiroItemCategory.CURRENCY: "Currency",
                         SekiroItemCategory.UPGRADE: "Upgrade",
                         SekiroItemCategory.HEALING: "Healing",
                     }[self.category])

        return names

    def counts(self, counts: List[int]) -> Generator["SekiroItemData", None, None]:
        """Returns an iterable of copies of this item with the given counts."""
        yield self
        for count in counts:
            yield dataclasses.replace(
                self,
                ap_code = None,
                name = "{} x{}".format(self.base_name, count),
                base_name = self.base_name,
                count = count,
                filler = False, # Don't count multiples as filler by default
            )

class SekiroItem(Item):
    game: str = "Sekiro: Shadows Die Twice"
    data: SekiroItemData

    def __init__(
            self,
            player: int,
            data: SekiroItemData,
            classification = None):
        super().__init__(data.name, classification or data.classification, data.ap_code, player)
        self.data = data

    @staticmethod
    def event(name: str, player: int) -> "SekiroItem":
        data = SekiroItemData(name, None, SekiroItemCategory.MISC,
                              skip = True, classification = ItemClassification.progression)
        data.ap_code = None
        return SekiroItem(player, data)


_all_items = [
    # Currency
    SekiroItemData("Light Coin Purse", 0xe74, SekiroItemCategory.CURRENCY, filler = True),
    SekiroItemData("Heavy Coin Purse", 0xe78, SekiroItemCategory.CURRENCY,
                   classification = ItemClassification.useful),
    SekiroItemData("Bulging Coin Purse", 0xe7c, SekiroItemCategory.CURRENCY,
                   classification = ItemClassification.useful),
    *SekiroItemData("Treasure Carp Scale", 0x2710, SekiroItemCategory.CURRENCY,
                    classification = ItemClassification.useful).counts([3, 5]),

    # Esoteric_texts
    SekiroItemData("Shinobi Esoteric Text", 0xb68, SekiroItemCategory.ESOTERIC_TEXTS,
                   classification = ItemClassification.useful),
    SekiroItemData("Prosthetic Esoteric Text", 0xb69, SekiroItemCategory.ESOTERIC_TEXTS,
                   classification = ItemClassification.useful),
    SekiroItemData("Ashina Esoteric Text", 0xb6a, SekiroItemCategory.ESOTERIC_TEXTS,
                   classification = ItemClassification.useful),
    SekiroItemData("Senpou Esoteric Text", 0xb6b, SekiroItemCategory.ESOTERIC_TEXTS,
                   classification = ItemClassification.useful),

    # Healing
    SekiroItemData("Prayer Bead", 0xfa0, SekiroItemCategory.HEALING),
    SekiroItemData("Gourd Seed", 0x1130, SekiroItemCategory.HEALING),

    # Incense
    SekiroItemData("Lotus of the Palace", 0x9c4, SekiroItemCategory.INCENSE,
                   classification = ItemClassification.progression),
    SekiroItemData("Shelter Stone", 0x9c5, SekiroItemCategory.INCENSE,
                   classification = ItemClassification.progression),
    SekiroItemData("Aromatic Branch", 0x9c6, SekiroItemCategory.INCENSE,
                   classification = ItemClassification.progression),

    # Memories
    SekiroItemData("Memory: Gyoubu Oniwa", 0x1450, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Lady Butterfly", 0x1451, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Genichiro", 0x1452, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Screen Monkeys", 0x1453, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Guardian Ape", 0x1454, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Corrupted Monk", 0x1455, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Great Shinobi", 0x1456, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Foster Father", 0x1457, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: True Monk", 0x1458, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Divine Dragon", 0x1459, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Hatred Demon", 0x145a, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    SekiroItemData("Memory: Saint Isshin", 0x145b, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),
    #For now injected as unreachable in regular ending.
    # redo when implementing alternate ending for Shura
    SekiroItemData("Memory: Isshin Ashina", 0x145c, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful, inject = True),
    SekiroItemData("Memory: Headless Ape", 0x145d, SekiroItemCategory.MEMORIES,
                   classification = ItemClassification.useful),

    # Misc
    *SekiroItemData("Pellet", 0xbcc, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    SekiroItemData("Divine Grass", 0xbe0, SekiroItemCategory.MISC),
    *SekiroItemData("Red Lump", 0xbea, SekiroItemCategory.MISC).counts([2]),
    SekiroItemData("Sweet Rice Ball x2", 0xbf4, SekiroItemCategory.MISC, count = 2),
    SekiroItemData("Persimmon", 0xbfe, SekiroItemCategory.MISC, classification = ItemClassification.progression),
    SekiroItemData("Rice", 0xc08, SekiroItemCategory.MISC, classification = ItemClassification.progression),
    SekiroItemData("Fine Snow", 0xc09, SekiroItemCategory.MISC, skip = True),
    *SekiroItemData("Antidote Powder", 0xc80, SekiroItemCategory.MISC, filler = True).counts([2]),
    *SekiroItemData("Dousing Powder", 0xc8a, SekiroItemCategory.MISC, filler = True).counts([2]),
    *SekiroItemData("Ministry Dousing Powder", 0xc8b, SekiroItemCategory.MISC).counts([2]),
    *SekiroItemData("Pacifying Agent", 0xc94, SekiroItemCategory.MISC,
                    classification = ItemClassification.useful).counts([2, 3, 5]),
    *SekiroItemData("Eel Liver", 0xc9e, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    *SekiroItemData("Contact Medicine", 0xcb2, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    *SekiroItemData("Bite Down", 0xcda, SekiroItemCategory.MISC, filler = True).counts([2]),
    *SekiroItemData("Ako's Sugar", 0xd48, SekiroItemCategory.MISC).counts([2, 3]),
    *SekiroItemData("Yashariku's Sugar", 0xd52, SekiroItemCategory.MISC).counts([2, 3]),
    *SekiroItemData("Ungo's Sugar", 0xd5c, SekiroItemCategory.MISC).counts([2, 3]),
    *SekiroItemData("Gokan's Sugar", 0xd66, SekiroItemCategory.MISC).counts([2, 3]),
    *SekiroItemData("Gachiin's Sugar", 0xd70, SekiroItemCategory.MISC).counts([2, 3]),
    *SekiroItemData("Divine Confetti", 0xd7a, SekiroItemCategory.MISC,
                    classification = ItemClassification.useful).counts([2, 3, 5]),
    *SekiroItemData("Ceramic Shard", 0xdac, SekiroItemCategory.MISC, filler = True).counts([2, 3, 4]),
    *SekiroItemData("Fistful of Ash", 0xdb6, SekiroItemCategory.MISC, filler = True).counts([2, 3, 5]),
    *SekiroItemData("Oil", 0xdc0, SekiroItemCategory.MISC, filler = True).counts([2, 3, 5]),
    *SekiroItemData("Snap Seed", 0xdca, SekiroItemCategory.MISC,
                   classification = ItemClassification.useful).counts([2, 3, 5]),
    *SekiroItemData("Mibu Balloon of Wealth", 0xe10, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    *SekiroItemData("Mibu Balloon of Soul", 0xe1a, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    *SekiroItemData("Mibu Possession Balloon", 0xe24, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    *SekiroItemData("Mibu Balloon of Spirit", 0xe2e, SekiroItemCategory.MISC, filler = True).counts([2, 3]),
    SekiroItemData("Bundled Jizo Statue", 0xe88, SekiroItemCategory.MISC,
                   classification = ItemClassification.useful),
    SekiroItemData("Dragon's Blood Droplet", 0x15e0, SekiroItemCategory.MISC,
                   classification = ItemClassification.useful),
    SekiroItemData("Ashina Sake", 0x238c, SekiroItemCategory.MISC),
    SekiroItemData("Unrefined Sake", 0x238d, SekiroItemCategory.MISC),
    SekiroItemData("Monkey Booze", 0x238e, SekiroItemCategory.MISC),
    SekiroItemData("Dragonspring Sake", 0x238f, SekiroItemCategory.MISC),
    SekiroItemData("Precious Bait", 0x23dc, SekiroItemCategory.MISC,
                   classification = ItemClassification.progression),

    # Skills
    SekiroItemData("Bloodsmoke Ninjutsu", 0x834, SekiroItemCategory.SKILLS),
    SekiroItemData("Puppeteer Ninjutsu", 0x83e, SekiroItemCategory.SKILLS,
                   classification=ItemClassification.progression),
    SekiroItemData("Bestowal Ninjutsu", 0x848, SekiroItemCategory.SKILLS),
    SekiroItemData("Mibu Breathing Technique", 0x974, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.progression),
    SekiroItemData("Anti-air Deathblow Text", 0x992, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),
    SekiroItemData("Dragon Flash", 0x99c, SekiroItemCategory.SKILLS),
    SekiroItemData("Shinobi Medicine Rank 1", 0x9a6, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),
    SekiroItemData("Floating Passage Text", 0x99d, SekiroItemCategory.SKILLS),
    SekiroItemData("Shinobi Medicine Rank 2", 0x9a7, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),
    # For now injected as unreachable in regular ending.
    # redo when implementing alternate ending for Shura
    SekiroItemData("One Mind", 0x99e, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Shinobi Medicine Rank 3", 0x9a8, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),
    SekiroItemData("A Beast's Karma", 0x9ab, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),
    SekiroItemData("Breath of Life: Shadow", 0x9b0, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),
    SekiroItemData("Breath of Nature: Shadow", 0x9b1, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful),

    # Unique
    SekiroItemData("Shinobi Prosthetic", 0x906, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Mortal Blade", 0x960, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Aromatic Flower", 0x9c7, SekiroItemCategory.UNIQUE),
    SekiroItemData("Mechanical Barrel", 0xb5e, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Sweet Rice Ball", 0xbf5, SekiroItemCategory.UNIQUE),
    SekiroItemData("Taro Persimmon", 0xbff, SekiroItemCategory.UNIQUE),
    SekiroItemData("Green Mossy Gourd", 0xce4, SekiroItemCategory.UNIQUE),
    SekiroItemData("Withered Red Gourd", 0xcee, SekiroItemCategory.UNIQUE),
    SekiroItemData("Mottled Purple Gourd", 0xcf8, SekiroItemCategory.UNIQUE),
    SekiroItemData("Ako's Spiritfall", 0xd16, SekiroItemCategory.UNIQUE),
    SekiroItemData("Yashariku's Spiritfall", 0xd20, SekiroItemCategory.UNIQUE),
    SekiroItemData("Ungo's Spiritfall", 0xd2a, SekiroItemCategory.UNIQUE),
    SekiroItemData("Gokan's Spiritfall", 0xd34, SekiroItemCategory.UNIQUE),
    SekiroItemData("Gachiin's Spiritfall", 0xd3e, SekiroItemCategory.UNIQUE),
    SekiroItemData("Five-color Rice", 0xdfc, SekiroItemCategory.UNIQUE),
    SekiroItemData("Mibu Pilgrimage Balloon", 0xe38, SekiroItemCategory.UNIQUE),
    SekiroItemData("Jinza's Jizo Statue", 0xe89, SekiroItemCategory.UNIQUE, inject = True),
    SekiroItemData("Ceremonial Tanto", 0xed8, SekiroItemCategory.UNIQUE),
    SekiroItemData("Nightjar Monocular", 0xf3c, SekiroItemCategory.UNIQUE),
    SekiroItemData("Mask Fragment: Right", 0x157c, SekiroItemCategory.UNIQUE),
    SekiroItemData("Mask Fragment: Left", 0x157d, SekiroItemCategory.UNIQUE),
    SekiroItemData("Mask Fragment: Dragon", 0x157e, SekiroItemCategory.UNIQUE),
    SekiroItemData("Divine Dragon's Tears", 0x2328, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Sakura Droplet", 0x2331, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Young Lord's Bell Charm", 0x2332, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Father's Bell Charm", 0x2333, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Ornamental Letter", 0x233c, SekiroItemCategory.UNIQUE),
    SekiroItemData("Red Carp Eyes", 0x235c, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Dragon's Tally Board", 0x2364, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Promissory Note", 0x2365, SekiroItemCategory.UNIQUE),
    SekiroItemData("Water of the Palace", 0x236e, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Great White Whisker", 0x236f, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Red and White Pinwheel", 0x2378, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("White Pinwheel", 0x2379, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Rice for Kuro", 0x2382, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Frozen Tears", 0x2383, SekiroItemCategory.UNIQUE),
    SekiroItemData("Truly Precious Bait (Harunaga)", 0x23dd, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Truly Precious Bait (Koremori)", 0x23de, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Fresh Serpent Viscera", 0x23e8, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Dried Serpent Viscera", 0x23e9, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Herb Catalogue Scrap", 0x23f0, SekiroItemCategory.UNIQUE),
    SekiroItemData("Dosaku's Note", 0x23f5, SekiroItemCategory.UNIQUE),
    SekiroItemData("Rat Description", 0x23f6, SekiroItemCategory.UNIQUE),
    SekiroItemData("Surgeon's Bloody Letter", 0x23f7, SekiroItemCategory.UNIQUE),
    SekiroItemData("Surgeon's Stained Letter", 0x23f8, SekiroItemCategory.UNIQUE),
    SekiroItemData("Holy Chapter: Dragon's Return", 0x23f9, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Immortal Severance Text", 0x23fa, SekiroItemCategory.UNIQUE),
    SekiroItemData("Immortal Severance Scrap", 0x23fb, SekiroItemCategory.UNIQUE),
    SekiroItemData("Fragrant Flower Note", 0x23fc, SekiroItemCategory.UNIQUE),
    SekiroItemData("Okami's Ancient Text", 0x23fd, SekiroItemCategory.UNIQUE),
    SekiroItemData("Page's Diary", 0x23fe, SekiroItemCategory.UNIQUE),
    SekiroItemData("Holy Chapter: Infested", 0x23ff, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Tomoe's Note", 0x2400, SekiroItemCategory.UNIQUE),
    SekiroItemData("Flame Barrel Memo", 0x2401, SekiroItemCategory.UNIQUE),
    SekiroItemData("Nightjar Beacon Memo", 0x2402, SekiroItemCategory.UNIQUE),
    SekiroItemData("Isshin's Letter", 0x2403, SekiroItemCategory.UNIQUE),
    SekiroItemData("Rotting Prisoner's Note", 0x2404, SekiroItemCategory.UNIQUE),
    SekiroItemData("Sabimaru Memo", 0x2405, SekiroItemCategory.UNIQUE),
    SekiroItemData("Valley Apparitions Memo", 0x2407, SekiroItemCategory.UNIQUE),
    SekiroItemData("Three-story Pagoda Memo", 0x2409, SekiroItemCategory.UNIQUE),
    SekiroItemData("Academics' Red Lump", 0xbed, SekiroItemCategory.UNIQUE),
    SekiroItemData("Hidden Tooth", 0xcdb, SekiroItemCategory.UNIQUE),
    SekiroItemData("Black Scroll", 0x240b, SekiroItemCategory.UNIQUE),
    SekiroItemData("Gatehouse Key", 0x24ba, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Hidden Temple Key", 0x24bb, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Secret Passage Key", 0x24bc, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Gun Fort Shrine Key", 0x24bd, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Shuriken Wheel", 0x25e4, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Phantom Kunai", 0x25e5, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Robert's Firecrackers", 0x25ee, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Flame Barrel", 0x25f8, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Pine Resin Ember", 0x25f9, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Shinobi Axe of the Monkey", 0x2602, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Mist Raven's Feathers", 0x260c, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.progression),
    SekiroItemData("Sabimaru", 0x2616, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Iron Fortress", 0x2620, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Large Fan", 0x262a, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Gyoubu's Broken Horn", 0x2634, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Slender Finger", 0x263e, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Malcontent's Ring", 0x263f, SekiroItemCategory.UNIQUE,
                   classification = ItemClassification.useful),
    SekiroItemData("Recovery Charm", 0xb72, SekiroItemCategory.UNIQUE, classification = ItemClassification.progression,
                   skip = True),

    # Upgrade
    *SekiroItemData("Scrap Iron", 0x1770, SekiroItemCategory.UPGRADE).counts([2, 3, 5]),
    *SekiroItemData("Scrap Magnetite", 0x177a, SekiroItemCategory.UPGRADE).counts([2, 3]),
    *SekiroItemData("Adamantite Scrap", 0x1784, SekiroItemCategory.UPGRADE).counts([2]),
    *SekiroItemData("Black Gunpowder", 0x17d4, SekiroItemCategory.UPGRADE).counts([2, 3]),
    *SekiroItemData("Yellow Gunpowder", 0x1838, SekiroItemCategory.UPGRADE).counts([2, 3, 4]),
    SekiroItemData("Fulminated Mercury", 0x1842, SekiroItemCategory.UPGRADE),
    *SekiroItemData("Lump of Fat Wax", 0x189c, SekiroItemCategory.UPGRADE).counts([2, 3]),
    *SekiroItemData("Lump of Grave Wax", 0x18a6, SekiroItemCategory.UPGRADE).counts([2]),
    *SekiroItemData("Lapis Lazuli", 0x1900, SekiroItemCategory.UPGRADE).counts([2]),

]

_skills_as_pickup = [
    # Skills usually obtained via Skill Tree. Keep for implementing option to also have them as item pickups.
    # This will have to be some sort of event pickup, as they have no actual item IDs.
    # Therefore, these are currently unused.
    SekiroItemData("Grappling Hook Attack", 0x30d40, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful, inject = True),
    SekiroItemData("Mid-air Deflection", 0x30da4, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Mid-air Prosthetic Tool", 0x30e08, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Mikiri Counter", 0x30e6c, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful, inject = True),
    SekiroItemData("Run and Slide", 0x30ed0, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Mid-air Combat Arts", 0x30f34, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Vault Over", 0x30f98, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Whirlwind Slash", 0x33450, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Shadowrush", 0x33838, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Chasing Slice", 0x497c8, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Fang and Blade", 0x4982c, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Projected Force", 0x49890, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Living Force", 0x498f4, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Nightjar Slash", 0x4baf0, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Nightjar Slash Reversal", 0x4bb54, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Ichimonji", 0x64190, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Ichimonji: Double", 0x641f4, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Ashina Cross", 0x645d8, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Praying Strikes", 0x7c7b0, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Praying Strikes - Exorcism", 0x7c814, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Senpou Leaping Kicks", 0x7cbf8, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("High Monk", 0x7cc5c, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Shadowfall", 0x95114, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Spiral Cloud Passage", 0x954fc, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Empowered Mortal Draw", 0x959e4, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Suppress Presence", 0x974a0, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Suppress Sound", 0x97504, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Virtuous Deed", 0x98160, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Most Virtuous Deed", 0x981c4, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Emma's Medicine: Potency", 0x9c400, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Emma's Medicine: Aroma", 0x9c464, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("A Shinobi's Karma: Body", 0x9e848, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("A Shinobi's Karma: Mind", 0x9e8ac, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Sculptor's Karma: Blood", 0x9e910, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Sculptor's Karma: Scars", 0x9e974, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Breath of Life: Light", 0xa1310, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Breath of Nature: Light", 0xa13d8, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Shinobi Eyes", 0xa14a0, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Devotion", 0xa1504, SekiroItemCategory.SKILLS, inject = True),
    SekiroItemData("Ascending Carp", 0xa1568, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful, inject = True),
    SekiroItemData("Descending Carp", 0xa15cc, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful, inject = True),
    SekiroItemData("Flowing Water", 0xa1630, SekiroItemCategory.SKILLS,
                   classification = ItemClassification.useful, inject = True),
]

item_name_groups: Dict[str, Set] = {
    "Esoteric Texts": set(),
    "Progression": set(),
    "Incense": set(),
    "Skills": set(),
    "Miscellaneous": set(),
    "Unique": set(),
    "Memories": set(),
    "Currency": set(),
    "Upgrade": set(),
    "Healing": set(),
}


item_descriptions = {
    "Esoteric Texts": "Items that unlock skill trees",
    "Skills": "Skills found outside Esoteric Texts, such as Shinobi Medicine and Ninjutsu",
    "Progression": "Items that unlock locations.",
    "Incense": "Items needed to reach Fountainhead Palace.",
    "Miscellaneous": "Generic stackable items, such as mibu balloons, ceramic shards, resistance buffs and so on.",
    "Unique": "Items that are unique in the playthrough, such as notes, keys, charms, reusables and so on. Doesn't include Skill Texts or Skills.",
    "Memories": "Memories dropped by major bosses to increase Attack Power.",
    "Currency": "Coin Purses and Treasure Carp Scales.",
    "Upgrade": "Non-unique materials to upgrade prosthetic tools.",
    "Healing": "Gourd Seeds and Prayer Beads.",
}

for item_data in _all_items:
    for group_name in item_data.item_groups():
        item_name_groups[group_name].add(item_data.name)

filler_item_names = [item_data.name for item_data in _all_items if item_data.filler]
item_dictionary = {item_data.name: item_data for item_data in _all_items}
