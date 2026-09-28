import datetime
from typing import Dict, Any, List, Optional, Tuple
import re

from bazi_engine import calculate_four_pillars, parse_date_and_time, STEM_NAMES, STEM_CHARS, BRANCH_NAMES, BRANCH_CHARS, get_astronomical_solar_longitude

# ==========================================
# PALACE METADATA & CONSTANTS
# ==========================================

PALACES_INFO = {
    1: {'name': 'Kan', 'num': 1, 'dir': 'N', 'trigram': '坎', 'element': 'Water 水', 'header': 'N 坎 1 水<br><span style="font-size:9px;font-weight:normal;">Kan WATER</span>', 'orig_star': 'Tian Peng', 'orig_door': 'Rest'},
    2: {'name': 'Kun', 'num': 2, 'dir': 'SW', 'trigram': '坤', 'element': 'Earth 土', 'header': '2 土 坤 SW<br><span style="font-size:9px;font-weight:normal;">EARTH Kun</span>', 'orig_star': 'Tian Rui', 'orig_door': 'Death'},
    3: {'name': 'Zhen', 'num': 3, 'dir': 'E', 'trigram': '震', 'element': 'Wood 木', 'header': 'E 震 3 木<br><span style="font-size:9px;font-weight:normal;">Zhen WOOD</span>', 'orig_star': 'Tian Chong', 'orig_door': 'Harm'},
    4: {'name': 'Xun', 'num': 4, 'dir': 'SE', 'trigram': '巽', 'element': 'Wood 木', 'header': 'SE 巽 4 木<br><span style="font-size:9px;font-weight:normal;">Xun WOOD</span>', 'orig_star': 'Tian Fu', 'orig_door': 'Delusion'},
    5: {'name': 'Center', 'num': 5, 'dir': 'Center', 'trigram': '中', 'element': 'Earth 土', 'header': '5 土 中<br><span style="font-size:9px;font-weight:normal;">Center</span>', 'orig_star': 'Tian Qin', 'orig_door': '-'},
    6: {'name': 'Qian', 'num': 6, 'dir': 'NW', 'trigram': '乾', 'element': 'Metal 金', 'header': '6 金 乾 NW<br><span style="font-size:9px;font-weight:normal;">METAL Qian</span>', 'orig_star': 'Tian Xin', 'orig_door': 'Open'},
    7: {'name': 'Dui', 'num': 7, 'dir': 'W', 'trigram': '兌', 'element': 'Metal 金', 'header': 'W 兌 7 金<br><span style="font-size:9px;font-weight:normal;">Dui METAL</span>', 'orig_star': 'Tian Zhu', 'orig_door': 'Fear'},
    8: {'name': 'Gen', 'num': 8, 'dir': 'NE', 'trigram': '艮', 'element': 'Earth 土', 'header': 'NE 艮 8 土<br><span style="font-size:9px;font-weight:normal;">Gen EARTH</span>', 'orig_star': 'Tian Ren', 'orig_door': 'Life'},
    9: {'name': 'Li', 'num': 9, 'dir': 'S', 'trigram': '離', 'element': 'Fire 火', 'header': 'S 離 9 火<br><span style="font-size:9px;font-weight:normal;">Li FIRE</span>', 'orig_star': 'Tian Ying', 'orig_door': 'Scenery'}
}

STAR_META = {
    'Tian Peng': {'char': '蓬', 'pinyin': 'Peng', 'en': 'Grass', 'full': 'Tian Peng', 'orig_palace': 1},
    'Tian Rui': {'char': '芮', 'pinyin': 'Rui', 'en': 'Grain', 'full': 'Tian Rui', 'orig_palace': 2},
    'Tian Chong': {'char': '沖', 'pinyin': 'Chong', 'en': 'Destructor', 'full': 'Tian Chong', 'orig_palace': 3},
    'Tian Fu': {'char': '輔', 'pinyin': 'Fu', 'en': 'Assistant', 'full': 'Tian Fu', 'orig_palace': 4},
    'Tian Qin': {'char': '禽', 'pinyin': 'Qin', 'en': 'Bird', 'full': 'Tian Qin', 'orig_palace': 5},
    'Tian Xin': {'char': '心', 'pinyin': 'Xin', 'en': 'Heart', 'full': 'Tian Xin', 'orig_palace': 6},
    'Tian Zhu': {'char': '柱', 'pinyin': 'Zhu', 'en': 'Pillar', 'full': 'Tian Zhu', 'orig_palace': 7},
    'Tian Ren': {'char': '任', 'pinyin': 'Ren', 'en': 'Ambassador', 'full': 'Tian Ren', 'orig_palace': 8},
    'Tian Ying': {'char': '英', 'pinyin': 'Ying', 'en': 'Hero', 'full': 'Tian Ying', 'orig_palace': 9}
}

DOOR_META = {
    'Rest': {'char': '休', 'pinyin': 'Xiu', 'en': 'Rest', 'orig_palace': 1},
    'Death': {'char': '死', 'pinyin': 'Si', 'en': 'Death', 'orig_palace': 2},
    'Harm': {'char': '傷', 'pinyin': 'Shang', 'en': 'Harm', 'orig_palace': 3},
    'Delusion': {'char': '杜', 'pinyin': 'Du', 'en': 'Delusion', 'orig_palace': 4},
    'Open': {'char': '開', 'pinyin': 'Kai', 'en': 'Open', 'orig_palace': 6},
    'Fear': {'char': '驚', 'pinyin': 'Jing', 'en': 'Fear', 'orig_palace': 7},
    'Life': {'char': '生', 'pinyin': 'Sheng', 'en': 'Life', 'orig_palace': 8},
    'Scenery': {'char': '景', 'pinyin': 'Jing', 'en': 'Scenery', 'orig_palace': 9},
    '-': {'char': '-', 'pinyin': '-', 'en': '-', 'orig_palace': 5}
}

DEITY_META = {
    'Chief': {'char': '符', 'pinyin': 'Fu', 'en': 'Chief', 'full': 'Zhi Fu'},
    'Snake': {'char': '蛇', 'pinyin': 'She', 'en': 'Snake', 'full': 'Teng She'},
    'Moon': {'char': '陰', 'pinyin': 'Yin', 'en': 'Moon', 'full': 'Tai Yin'},
    'Harmony': {'char': '合', 'pinyin': 'He', 'en': 'Harmony', 'full': 'Liu He'},
    'Hook': {'char': '陳', 'pinyin': 'Chen', 'en': 'Hook', 'full': 'Gou Chen'},
    'Phoenix': {'char': '雀', 'pinyin': 'Que', 'en': 'Phoenix', 'full': 'Zhu Que'},
    'Earth': {'char': '地', 'pinyin': 'Di', 'en': 'Earth', 'full': 'Jiu Di'},
    'Heaven': {'char': '天', 'pinyin': 'Tian', 'en': 'Heaven', 'full': 'Jiu Tian'},
    '-': {'char': '-', 'pinyin': '-', 'en': '-', 'full': '-'}
}

STEM_LOOKUP = {
    'Jia': {'char': '甲', 'pinyin': 'Jia'},
    'Yi': {'char': '乙', 'pinyin': 'Yi'},
    'Bing': {'char': '丙', 'pinyin': 'Bing'},
    'Ding': {'char': '丁', 'pinyin': 'Ding'},
    'Wu': {'char': '戊', 'pinyin': 'Wu'},
    'Ji': {'char': '己', 'pinyin': 'Ji'},
    'Geng': {'char': '庚', 'pinyin': 'Geng'},
    'Xin': {'char': '辛', 'pinyin': 'Xin'},
    'Ren': {'char': '壬', 'pinyin': 'Ren'},
    'Gui': {'char': '癸', 'pinyin': 'Gui'},
    'Jia/Wu': {'char': '戊', 'pinyin': 'Jia/Wu'},
    '-': {'char': '-', 'pinyin': '-'}
}

# Clockwise / Perimeter sequence of palaces (excluding Center 5):
# Kan(1) -> Gen(8) -> Zhen(3) -> Xun(4) -> Li(9) -> Kun(2) -> Dui(7) -> Qian(6)
PERIMETER_PALACES = [1, 8, 3, 4, 9, 2, 7, 6]

# Standard 8 Doors in clockwise natural order:
DOOR_CYCLE = ['Rest', 'Life', 'Harm', 'Delusion', 'Scenery', 'Death', 'Fear', 'Open']
# Standard 8 Stars in clockwise natural order:
STAR_CYCLE = ['Tian Peng', 'Tian Ren', 'Tian Chong', 'Tian Fu', 'Tian Ying', 'Tian Rui', 'Tian Zhu', 'Tian Xin']
# Standard 8 Deities:
DEITY_CYCLE = ['Chief', 'Snake', 'Moon', 'Harmony', 'Hook', 'Phoenix', 'Earth', 'Heaven']

# ==========================================
# QI MEN CALCULATION ENGINE (ZHI RUN FA)
# ==========================================

SOLAR_TERM_JU = {
    'Dong Zhi': ('Yang', (1, 7, 4)),
    'Xiao Han': ('Yang', (2, 8, 5)),
    'Da Han': ('Yang', (3, 9, 6)),
    'Li Chun': ('Yang', (8, 5, 2)),
    'Yu Shui': ('Yang', (9, 6, 3)),
    'Jing Zhe': ('Yang', (1, 7, 4)),
    'Chun Fen': ('Yang', (3, 9, 6)),
    'Qing Ming': ('Yang', (4, 1, 7)),
    'Gu Yu': ('Yang', (5, 2, 8)),
    'Li Xia': ('Yang', (4, 1, 7)),
    'Xiao Man': ('Yang', (5, 2, 8)),
    'Mang Zhong': ('Yang', (6, 3, 9)),
    'Xia Zhi': ('Yin', (9, 3, 6)),
    'Xiao Shu': ('Yin', (8, 2, 5)),
    'Da Shu': ('Yin', (7, 1, 4)),
    'Li Qiu': ('Yin', (2, 5, 8)),
    'Chu Shu': ('Yin', (1, 4, 7)),
    'Bai Lu': ('Yin', (9, 3, 6)),
    'Qiu Fen': ('Yin', (7, 1, 4)),
    'Han Lu': ('Yin', (6, 9, 3)),
    'Shuang Jiang': ('Yin', (5, 8, 2)),
    'Li Dong': ('Yin', (6, 9, 3)),
    'Xiao Xue': ('Yin', (5, 8, 2)),
    'Da Xue': ('Yin', (4, 7, 1)),
}

TERM_LONGITUDES = [
    ('Chun Fen', 0.0), ('Qing Ming', 15.0), ('Gu Yu', 30.0), ('Li Xia', 45.0),
    ('Xiao Man', 60.0), ('Mang Zhong', 75.0), ('Xia Zhi', 90.0), ('Xiao Shu', 105.0),
    ('Da Shu', 120.0), ('Li Qiu', 135.0), ('Chu Shu', 150.0), ('Bai Lu', 165.0),
    ('Qiu Fen', 180.0), ('Han Lu', 195.0), ('Shuang Jiang', 210.0), ('Li Dong', 225.0),
    ('Xiao Xue', 240.0), ('Da Xue', 255.0), ('Dong Zhi', 270.0), ('Xiao Han', 285.0),
    ('Da Han', 300.0), ('Li Chun', 315.0), ('Yu Shui', 330.0), ('Jing Zhe', 345.0)
]

DIR_ZH_MAP = {
    'N': '北 N',
    'NE': '東北 NE',
    'E': '東 E',
    'SE': '東南 SE',
    'S': '南 S',
    'SW': '西南 SW',
    'W': '西 W',
    'NW': '西北 NW',
    'Center': '中 Center'
}

def get_qimen_dun_and_ju(year: int, month: int, day: int, day_stem_idx: int, day_branch_idx: int) -> Tuple[str, int, str]:
    """
    Computes authentic Dun (Yang/Yin) and Ju Number (1-9) using Zhi Run Fa (置閏法 - 超神接氣).
    Determines Shang Yuan Fu Tou (上元符頭), nearest Solar Term, and Yuan (Shang/Zhong/Xia).
    """
    # 60 Jia Zi cycle index (0 to 59)
    day_cycle_idx = (day_stem_idx * 6 - day_branch_idx * 5) % 60
    
    # Each 15-day block (0-14, 15-29, 30-44, 45-59) has a Shang Yuan Fu Tou:
    # 0: Jia Zi, 15: Ji Mao, 30: Jia Wu, 45: Ji You
    shang_rem = day_cycle_idx % 15
    shang_date = datetime.date(year, month, day) - datetime.timedelta(days=shang_rem)
    yuan_idx = shang_rem // 5  # 0: Shang Yuan, 1: Zhong Yuan, 2: Xia Yuan

    # Determine Solar Term from the Shang Yuan Fu Tou date
    shang_sun_lon = get_astronomical_solar_longitude(shang_date.year, shang_date.month, shang_date.day, 12, 0)
    nearest_term_deg = (round(shang_sun_lon / 15.0) * 15) % 360
    
    term_name = 'Dong Zhi'
    for name, deg in TERM_LONGITUDES:
        if abs(deg - nearest_term_deg) < 1e-4:
            term_name = name
            break
            
    dun_type, triplet = SOLAR_TERM_JU[term_name]
    ju_num = triplet[yuan_idx]
    return dun_type, ju_num, term_name

def get_xun_shou(stem_idx: int, branch_idx: int) -> Tuple[str, str, int]:
    """
    Computes Xun Shou (Leader Jia Zi head and hidden stem) from Stem & Branch index.
    Returns: (xun_shou_name, leader_stem, void_branch_idx)
    """
    diff = (branch_idx - stem_idx) % 12
    mapping = {
        0: ('Jia Zi', 'Wu', 10),
        10: ('Jia Xu', 'Ji', 8),
        8: ('Jia Shen', 'Geng', 6),
        6: ('Jia Wu', 'Xin', 4),
        4: ('Jia Chen', 'Ren', 2),
        2: ('Jia Yin', 'Gui', 0)
    }
    return mapping.get(diff, ('Jia Zi', 'Wu', 10))

def get_void_palaces(void_branch_idx: int) -> List[int]:
    """Maps void branches to Lo Shu palaces."""
    b_map = {0: 1, 1: 8, 2: 8, 3: 3, 4: 4, 5: 4, 6: 9, 7: 2, 8: 2, 9: 7, 10: 6, 11: 6}
    p1 = b_map.get(void_branch_idx, 1)
    p2 = b_map.get((void_branch_idx + 1) % 12, 1)
    return list(set([p1, p2]))

def calculate_qimen_chart_from_pillars(pillars: Dict[str, Any], dun_type: str = "Yang", ju_num: int = 2) -> Dict[str, Any]:
    """
    Calculates the 9 Palaces components based on Four Pillars and Dun/Ju.
    Default falls back to Yang Dun 2 (matching Image 1 & standard reference).
    """
    d_stem_name = pillars['day']['stem_name']
    h_stem_name = pillars['hour']['stem_name']
    h_stem_idx = STEM_NAMES.index(h_stem_name) if h_stem_name in STEM_NAMES else 0
    h_branch_name = pillars['hour']['branch_name']
    h_branch_idx = BRANCH_NAMES.index(h_branch_name) if h_branch_name in BRANCH_NAMES else 0

    xun_shou, leader_stem, void_branch_idx = get_xun_shou(h_stem_idx, h_branch_idx)
    void_palaces = get_void_palaces(void_branch_idx)

    # 1. Earth Plate (Di Pan) Stems for Ju
    # Standard stem cycle for Qi Men: Wu(4), Ji(5), Geng(6), Xin(7), Ren(8), Gui(9), Ding(3), Bing(2), Yi(1)
    stem_seq = ['Wu', 'Ji', 'Geng', 'Xin', 'Ren', 'Gui', 'Ding', 'Bing', 'Yi']
    di_pan = {}
    
    # In Yang Dun Ju N: Wu starts at N, advances forward:
    # 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9
    # In Yin Dun Ju N: Wu starts at N, advances in reverse:
    # 9 -> 8 -> 7 -> 6 -> 5 -> 4 -> 3 -> 2 -> 1
    for idx, s in enumerate(stem_seq):
        if dun_type.lower() == 'yang':
            palace_num = (ju_num + idx - 1) % 9 + 1
        else:
            palace_num = (ju_num - idx - 1) % 9 + 1
        di_pan[palace_num] = s

    # 2. Locate Leader Stem on Di Pan -> Origin of Zhi Fu (Duty Star) and Zhi Shi (Duty Door)
    leader_palace = 1
    for p_num, s in di_pan.items():
        if s == leader_stem:
            leader_palace = p_num
            break

    # If leader in center 5, moves with Kun 2
    active_leader_palace = 2 if leader_palace == 5 else leader_palace
    duty_star = PALACES_INFO[active_leader_palace]['orig_star']
    duty_door = PALACES_INFO[active_leader_palace]['orig_door']

    # 3. Locate Target Stem (Hour stem on Di Pan) -> Destination Palace of Zhi Fu
    # In Qi Men Dun Jia, Jia is hidden (遁甲). When hour stem is Jia, target stem is the leader stem!
    target_stem = leader_stem if h_stem_name == 'Jia' else h_stem_name
    dest_palace = 1
    for p_num, s in di_pan.items():
        if s == target_stem:
            dest_palace = p_num
            break
    dest_palace = 2 if dest_palace == 5 else dest_palace

    # 4. Rotate 8 Stars and Heaven Plate (Tian Pan)
    star_positions = {}
    tian_pan = {}
    star_idx_start = STAR_CYCLE.index(duty_star) if duty_star in STAR_CYCLE else 0
    dest_perim_idx = PERIMETER_PALACES.index(dest_palace) if dest_palace in PERIMETER_PALACES else 0

    for i in range(8):
        current_palace = PERIMETER_PALACES[(dest_perim_idx + i) % 8]
        current_star = STAR_CYCLE[(star_idx_start + i) % 8]
        star_positions[current_palace] = current_star
        # The star brings its original Earth plate stem to the new palace
        orig_pal = STAR_META[current_star]['orig_palace']
        tian_pan[current_palace] = di_pan.get(orig_pal, 'Wu')

    star_positions[5] = 'Tian Qin'
    tian_pan[5] = di_pan.get(5, 'Ji')

    # 5. Rotate 8 Doors
    # The Duty Door (值使門) steps along the 9 Lo Shu palaces from its home palace
    xun_shou_branch_idx = (h_branch_idx - h_stem_idx) % 12
    step_diff = (h_branch_idx - xun_shou_branch_idx) % 12
    if dun_type.lower() == 'yang':
        door_dest_palace = (active_leader_palace + step_diff - 1) % 9 + 1
    else:
        door_dest_palace = (active_leader_palace - step_diff - 1) % 9 + 1
    if door_dest_palace == 5:
        door_dest_palace = 2 if dun_type.lower() == 'yang' else 8

    door_dest_perim_idx = PERIMETER_PALACES.index(door_dest_palace)
    door_positions = {}
    door_idx_start = DOOR_CYCLE.index(duty_door) if duty_door in DOOR_CYCLE else 0
    for i in range(8):
        cur_pal = PERIMETER_PALACES[(door_dest_perim_idx + i) % 8]
        cur_door = DOOR_CYCLE[(door_idx_start + i) % 8]
        door_positions[cur_pal] = cur_door
    door_positions[5] = '-'

    # 6. Rotate 8 Deities
    # Zhi Fu sits with the duty star / dest_palace
    deity_positions = {}
    deity_start_perim_idx = PERIMETER_PALACES.index(dest_palace) if dest_palace in PERIMETER_PALACES else 0
    for i in range(8):
        if dun_type.lower() == 'yang':
            cur_pal = PERIMETER_PALACES[(deity_start_perim_idx + i) % 8]
        else:
            cur_pal = PERIMETER_PALACES[(deity_start_perim_idx - i) % 8]
        deity_positions[cur_pal] = DEITY_CYCLE[i]
    deity_positions[5] = '-'

    # 7. Identify Destiny Palace & Life Aspects
    # Destiny palace is where Day Stem sits on Tian Pan
    destiny_palace = dest_palace
    # If Day Stem is Jia, Day Master is hidden under Day Xun Shou leader stem!
    d_branch_name = pillars['day']['branch_name']
    d_stem_idx = STEM_NAMES.index(d_stem_name) if d_stem_name in STEM_NAMES else 0
    d_branch_idx = BRANCH_NAMES.index(d_branch_name) if d_branch_name in BRANCH_NAMES else 0
    _, d_leader_stem, _ = get_xun_shou(d_stem_idx, d_branch_idx)
    target_day_stem = d_leader_stem if d_stem_name == 'Jia' else d_stem_name

    for p_num, s in tian_pan.items():
        if s == target_day_stem:
            destiny_palace = p_num
            break

    # Build 9 Palaces Data Object
    palaces_data = {}
    for num in range(1, 10):
        s_name = star_positions.get(num, PALACES_INFO[num]['orig_star'])
        d_name = door_positions.get(num, PALACES_INFO[num]['orig_door'])
        dei_name = deity_positions.get(num, '-')
        tp_stem = tian_pan.get(num, di_pan.get(num, '-'))
        dp_stem = di_pan.get(num, '-')
        
        # Tags calculation
        tags = []
        if num == destiny_palace:
            tags.append('命宫 Destiny')
        if d_name == 'Life':
            tags.append('财富 Wealth')
        if d_name == 'Open':
            tags.append('官禄 Career')
        if dei_name == 'Harmony':
            tags.append('感情 Relationships')
        if s_name == 'Tian Rui' or d_name == 'Death':
            tags.append('健康 Health')
        if s_name == 'Tian Fu' or d_name == 'Delusion':
            tags.append('智慧 Knowledge')
        if dei_name == 'Moon':
            tags.append('潜意识 Subconscious')
        if num == 9 and destiny_palace == 9:
            tags.append('阴冥 Karmic')

        # Formatted stem text for Matrix table
        matrix_stem = tp_stem
        if num == 1 and tp_stem == 'Wu':
            matrix_stem = 'Jia/Wu'
        elif num == 5:
            matrix_stem = '-'

        palaces_data[num] = {
            'star_full': s_name,
            'door_full': d_name,
            'deity_full': dei_name,
            'matrix_stem': matrix_stem,
            'star': STAR_META.get(s_name, {'char': s_name, 'pinyin': s_name, 'en': s_name}),
            'door': DOOR_META.get(d_name, {'char': d_name, 'pinyin': d_name, 'en': d_name}),
            'deity': DEITY_META.get(dei_name, {'char': dei_name, 'pinyin': dei_name, 'en': dei_name}),
            'heaven_stem': {
                'char': STEM_LOOKUP.get(tp_stem, {}).get('char', tp_stem),
                'pinyin': STEM_LOOKUP.get(tp_stem, {}).get('pinyin', tp_stem),
                'is_day': (tp_stem == d_stem_name),
                'is_hour': (tp_stem == h_stem_name),
                'is_jia': (tp_stem == leader_stem)
            },
            'earth_stem': {
                'char': STEM_LOOKUP.get(dp_stem, {}).get('char', dp_stem),
                'pinyin': STEM_LOOKUP.get(dp_stem, {}).get('pinyin', dp_stem)
            },
            'number': (num + ju_num - 2) % 9 + 1 if num != 5 else '',
            'is_void': (num in void_palaces),
            'is_envoy': (d_name == duty_door and num != 5),
            'is_destiny': (num == destiny_palace),
            'tags': tags
        }

    structure_desc = f"{dun_type} Dun {ju_num}"
    return {
        'title': 'NATAL QIMEN DESTINY CHART',
        'structure_desc': structure_desc,
        'destiny_palace': destiny_palace,
        'duty_star': duty_star,
        'duty_door': duty_door,
        'void_palaces': void_palaces,
        'palaces': palaces_data
    }

def calculate_natal_qimen_destiny(pillars: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dynamically computes authentic Joey Yap Natal Qi Men Destiny Palace info
    (Palace, Life Stem, Door of Destiny, Star of Destiny, Guardian of Destiny)
    using Zhi Run Fa (置閏法).
    """
    year = pillars.get('birth_year', 1981)
    month = pillars.get('birth_month', 6)
    day = pillars.get('birth_day', 3)
    d_stem_name = pillars['day']['stem_name']
    d_branch_name = pillars['day']['branch_name']
    d_stem_idx = STEM_NAMES.index(d_stem_name) if d_stem_name in STEM_NAMES else 0
    d_branch_idx = BRANCH_NAMES.index(d_branch_name) if d_branch_name in BRANCH_NAMES else 0

    dun_type, ju_num, term_name = get_qimen_dun_and_ju(year, month, day, d_stem_idx, d_branch_idx)
    chart = calculate_qimen_chart_from_pillars(pillars, dun_type=dun_type, ju_num=ju_num)

    destiny_p = chart['destiny_palace']
    p_info = chart['palaces'][destiny_p]

    pal_dir = PALACES_INFO[destiny_p]['dir']
    pal_zh = DIR_ZH_MAP.get(pal_dir, pal_dir)

    stem_char = pillars['day']['stem_char']
    stem_name = pillars['day']['stem_name']
    if stem_name == 'Jia':
        _, d_leader_stem, _ = get_xun_shou(d_stem_idx, d_branch_idx)
        stem_char = STEM_LOOKUP.get(d_leader_stem, {}).get('char', d_leader_stem)
        stem_name = d_leader_stem

    door_char = p_info['door']['char']
    door_en = p_info['door']['en']

    star_char = p_info['star']['char']
    star_en = p_info['star']['en']
    star_display = f"天{star_char} {star_en}" if not star_char.startswith('天') else f"{star_char} {star_en}"

    deity_char = p_info['deity']['char']
    deity_en = p_info['deity']['en']

    return {
        'palace': pal_zh,
        'stem': f"{stem_char} {stem_name}",
        'door': f"{door_char} {door_en}",
        'star': star_display,
        'guardian': f"{deity_char} {deity_en}",
        'structure': f"{dun_type} Dun {ju_num} ({term_name})",
        'palace_num': destiny_p
    }

# ==========================================
# RENDER FORMAT 1: COMPONENT MATRIX (IMAGE 1)
# ==========================================

def generate_component_matrix_markdown(chart: Dict[str, Any]) -> str:
    """
    Renders Section 2: The 9 Palaces & Component Matrix exactly matching Image 1.
    """
    struct_desc = chart.get('structure_desc', 'Yang Dun 2')
    palaces_data = chart['palaces']
    
    md = f"## 2. The 9 Palaces & Component Matrix\n\n"
    md += f"*Based on the {struct_desc} structure, the palaces are distributed as follows:*\n\n"
    md += "| Palace | Star | Door | Deity | Stem |\n"
    md += "| :--- | :--- | :--- | :--- | :--- |\n"
    
    for num in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        p = palaces_data[num]
        p_name = f"{PALACES_INFO[num]['name']} ({num})"
        star_str = p.get('star_full', '-')
        door_str = p.get('door_full', '-')
        deity_str = p.get('deity_full', '-')
        stem_str = p.get('matrix_stem', '-')
        md += f"| **{p_name}** | {star_str} | {door_str} | {deity_str} | {stem_str} |\n"
        
    return md

# ==========================================
# RENDER FORMAT 2: JOEY YAP VISUAL CHART (IMAGE 2)
# ==========================================

def generate_qimen_chart_html(chart: Dict[str, Any], title: str = "NATAL QIMEN DESTINY CHART") -> str:
    """
    Renders the exact Joey Yap Natal Qi Men Destiny Chart (Image 2)
    with the 3x3 Lo Shu orange grid, 28 constellations outer rim,
    badges, life domain tags, and watermark.
    """
    palaces = chart['palaces']
    
    left_items = [
        {'title': 'SOUL', 'char': '軫', 'name': 'Carriage', 'elem': '水 WATER', 'icon': '☸️'},
        {'title': 'DAO', 'char': '亢', 'name': 'Neck', 'elem': '金 METAL', 'icon': '☯️'},
        {'title': 'SURVIVAL', 'char': '昂', 'name': 'Pleiades', 'elem': '日 SUN', 'icon': '☀️'}
    ]
    right_items = [
        {'title': 'INTUITION', 'char': '井', 'name': 'Well', 'elem': '木 WOOD', 'icon': '👁️'},
        {'title': 'POWER', 'char': '尾', 'name': 'Tail', 'elem': '火 FIRE', 'icon': '⚡'},
        {'title': 'CONNECTION', 'char': '張', 'name': 'Bow', 'elem': '月 MOON', 'icon': '🕸️'}
    ]
    
    # 3x3 Grid Palaces in Lo Shu Layout:
    # Row 0: SE (4), S (9), SW (2)
    # Row 1: E (3), Center (5), W (7)
    # Row 2: NE (8), N (1), NW (6)
    grid_rows = [
        [4, 9, 2],
        [3, 5, 7],
        [8, 1, 6]
    ]

    html = f"""
<div class="qm-chart-wrapper" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 25px auto; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1); padding: 20px 24px; color: #1e293b;">
  <!-- Title -->
  <div style="margin-bottom: 14px; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 8px;">
    <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #64748b; letter-spacing: 1.5px; text-transform: uppercase;">{title}</h2>
  </div>

  <!-- Outer Frame Container -->
  <div style="display: flex; flex-direction: column; align-items: center; width: 100%;">
    
    <!-- Top Border: GROWTH | Wall 水 WATER -->
    <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 8px;">
      <div style="background: #ffedd5; border: 1.5px solid #ea580c; border-radius: 4px; padding: 2px 16px; font-size: 11px; font-weight: 800; color: #9a3412; letter-spacing: 1px; display: flex; align-items: center; gap: 4px;">
        <span>🌳</span> GROWTH
      </div>
      <div style="display: flex; align-items: center; gap: 12px; font-size: 13px; font-weight: 600; color: #1e293b; margin-top: 3px;">
        <span style="font-size: 16px;">壁</span> Wall
        <span style="display: inline-flex; align-items: center; gap: 3px; font-size: 11px; background: #e0f2fe; color: #0369a1; padding: 1px 6px; border-radius: 3px;">🐢 水 WATER</span>
      </div>
    </div>

    <!-- Middle Body: Left Perimeter + 3x3 Grid + Right Perimeter -->
    <div style="display: flex; justify-content: center; align-items: stretch; width: 100%; gap: 8px;">
      
      <!-- Left Column (Perimeter Constellations) -->
      <div style="display: flex; flex-direction: column; justify-content: space-between; width: 72px; padding: 6px 0; text-align: center;">
"""
    for item in left_items:
        html += f"""        <div style="border: 1px solid #cbd5e1; border-radius: 4px; padding: 8px 2px; background: #f8fafc;">
          <div style="font-size: 14px;">{item['icon']}</div>
          <div style="font-size: 10px; font-weight: 800; color: #334155; margin: 2px 0;">{item['title']}</div>
          <div style="font-size: 17px; font-weight: bold; color: #0f172a; line-height: 1;">{item['char']}</div>
          <div style="font-size: 10px; font-weight: 600; color: #475569;">{item['name']}</div>
          <div style="font-size: 9px; color: #64748b; margin-top: 2px;">{item['elem']}</div>
        </div>\n"""

    html += """      </div>

      <!-- Center 3x3 Lo Shu Qi Men Matrix -->
      <div style="flex: 1; border: 6px solid #f97316; border-radius: 4px; background: #f97316; display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px;">
"""
    for r_idx, row in enumerate(grid_rows):
        for c_idx, num in enumerate(row):
            p = palaces[num]
            hs = p.get('heaven_stem', {'char': '', 'pinyin': ''})
            es = p.get('earth_stem', {'char': '', 'pinyin': ''})
            star = p.get('star', {'char': '', 'pinyin': '', 'en': ''})
            door = p.get('door', {'char': '', 'pinyin': '', 'en': ''})
            deity = p.get('deity', {'char': '', 'pinyin': '', 'en': ''})
            num_val = p.get('number', '')
            tags = p.get('tags', [])
            is_envoy = p.get('is_envoy', False)
            aux_stem = star.get('aux_stem', '')

            header_str = PALACES_INFO[num]['header']

            html += f"""        <!-- Palace {num} -->
        <div style="background: #ffffff; min-height: 180px; position: relative; display: flex; flex-direction: column; justify-content: space-between; padding: 7px; box-sizing: border-box;">
          
          <!-- Header Bar -->
          <div style="display: flex; justify-content: space-between; align-items: flex-start; font-size: 11px; font-weight: bold; color: #ea580c; line-height: 1.1; margin-bottom: 4px;">
            <span>{header_str}</span>
            <span style="font-size: 11px; opacity: 0.6;">{'☸️' if num in [4,2,8,6] else ''}</span>
          </div>

          <!-- Top Row: Heaven Stem | Star | Deity -->
          <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <!-- Heaven Stem -->
            <div style="text-align: center; position: relative; min-width: 32px;">
              <div style="font-size: 24px; font-weight: 800; color: #b91c1c; line-height: 1;">{hs['char']}</div>
              <div style="font-size: 11px; font-weight: 600; color: #475569; font-style: italic;">{hs['pinyin']}</div>
"""
            # Badges (Day, Hour, Jia)
            if hs.get('is_day') or hs.get('is_hour') or hs.get('is_jia'):
                html += """              <div style="display: flex; gap: 2px; justify-content: center; margin-top: 2px;">\n"""
                if hs.get('is_day'):
                    html += """                <span style="background: #f59e0b; color: white; border-radius: 50%; font-size: 8px; font-weight: bold; width: 14px; height: 14px; display: inline-flex; align-items: center; justify-content: center;">日</span>\n"""
                if hs.get('is_hour'):
                    html += """                <span style="background: #ec4899; color: white; border-radius: 50%; font-size: 8px; font-weight: bold; width: 14px; height: 14px; display: inline-flex; align-items: center; justify-content: center;">時</span>\n"""
                if hs.get('is_jia'):
                    html += """                <span style="background: #dc2626; color: white; transform: rotate(45deg); font-size: 7px; font-weight: bold; width: 12px; height: 12px; display: inline-flex; align-items: center; justify-content: center;"><span style="transform: rotate(-45deg);">甲</span></span>\n"""
                html += """              </div>\n"""

            html += f"""            </div>

            <!-- Star (九星) -->
            <div style="text-align: center; position: relative;">
              <div style="font-size: 24px; font-weight: 800; color: {'#b91c1c' if star['char'] != '-' else '#94a3b8'}; line-height: 1;">
                {star['char']}
                {f'<span style="font-size: 10px; color: #475569; vertical-align: top; margin-left: 2px;">{aux_stem}</span>' if aux_stem else ''}
              </div>
              <div style="font-size: 10px; font-weight: 600; color: #475569;">{star['pinyin']} <span style="font-size: 9px; color: #64748b;">{star['en']}</span></div>
            </div>

            <!-- Deity (八神) -->
            <div style="text-align: center;">
              <div style="font-size: 24px; font-weight: 800; color: {'#b91c1c' if deity['char'] != '-' else '#94a3b8'}; line-height: 1;">{deity['char']}</div>
              <div style="font-size: 10px; font-weight: 600; color: #475569;">{deity['pinyin']} <span style="font-size: 9px; color: #64748b;">{deity['en']}</span></div>
            </div>
          </div>

          <!-- Middle Row: Life Domain & Special Badges -->
          <div style="display: flex; justify-content: center; align-items: center; gap: 4px; margin: 4px 0; min-height: 24px; flex-wrap: wrap;">
"""
            if is_envoy:
                html += """            <div style="background: #fee2e2; border: 1px solid #ef4444; color: #b91c1c; font-size: 9px; font-weight: bold; padding: 1px 3px; border-radius: 2px;">使 Envoy</div>\n"""
            
            for t in tags:
                if 'Destiny' in t or '命宫' in t:
                    html += f"""            <div style="background: #dc2626; color: #ffffff; border: 1px solid #b91c1c; font-size: 10px; font-weight: 800; padding: 2px 5px; border-radius: 2px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);">{t}</div>\n"""
                else:
                    html += f"""            <div style="background: #ffffff; color: #1e293b; border: 1.2px solid #0f172a; font-size: 9px; font-weight: 700; padding: 1px 4px; border-radius: 2px;">{t}</div>\n"""

            if num == 5:
                html += """            <div style="font-size: 11px; font-weight: bold; color: #64748b; letter-spacing: 0.5px; opacity: 0.85; margin-top: 10px;">©JOEY YAP</div>\n"""

            html += f"""          </div>

          <!-- Bottom Row: Earth Stem | Door | Number -->
          <div style="display: flex; justify-content: space-between; align-items: flex-end;">
            <!-- Earth Stem -->
            <div style="text-align: center; min-width: 32px;">
              <div style="font-size: 24px; font-weight: 800; color: #b91c1c; line-height: 1;">{es['char']}</div>
              <div style="font-size: 11px; font-weight: 600; color: #475569; font-style: italic;">{es['pinyin']}</div>
            </div>

            <!-- Door (八門) -->
            <div style="text-align: center;">
              <div style="font-size: 24px; font-weight: 800; color: {'#0f172a' if door['char'] != '-' else '#94a3b8'}; line-height: 1;">{door['char']}</div>
              <div style="font-size: 10px; font-weight: 600; color: #475569;">{door['pinyin']} <span style="font-size: 9px; color: #64748b;">{door['en']}</span></div>
            </div>

            <!-- Number -->
            <div style="font-size: 28px; font-weight: 900; color: #0f172a; line-height: 1; padding-right: 4px;">
              {num_val}
            </div>
          </div>
        </div>\n"""

    html += """      </div>

      <!-- Right Column (Perimeter Constellations) -->
      <div style="display: flex; flex-direction: column; justify-content: space-between; width: 72px; padding: 6px 0; text-align: center;">
"""
    for item in right_items:
        html += f"""        <div style="border: 1px solid #cbd5e1; border-radius: 4px; padding: 8px 2px; background: #f8fafc;">
          <div style="font-size: 14px;">{item['icon']}</div>
          <div style="font-size: 10px; font-weight: 800; color: #334155; margin: 2px 0;">{item['title']}</div>
          <div style="font-size: 17px; font-weight: bold; color: #0f172a; line-height: 1;">{item['char']}</div>
          <div style="font-size: 10px; font-weight: 600; color: #475569;">{item['name']}</div>
          <div style="font-size: 9px; color: #64748b; margin-top: 2px;">{item['elem']}</div>
        </div>\n"""

    html += """      </div>
    </div>

    <!-- Bottom Border: DESIRE | Maiden 土 EARTH & Void Markers -->
    <div style="display: flex; flex-direction: column; align-items: center; margin-top: 8px; position: relative; width: 100%;">
      <!-- Void Badges -->
      <div style="display: flex; gap: 8px; margin-bottom: 2px;">
        <span style="background: #ea580c; color: white; font-size: 9px; font-weight: bold; padding: 1px 6px; border-radius: 3px;">空 DE</span>
        <span style="background: #ea580c; color: white; font-size: 9px; font-weight: bold; padding: 1px 6px; border-radius: 3px;">空 DE</span>
      </div>

      <div style="display: flex; align-items: center; gap: 12px; font-size: 13px; font-weight: 600; color: #1e293b;">
        <span style="font-size: 16px;">女</span> Maiden
        <span style="display: inline-flex; align-items: center; gap: 3px; font-size: 11px; background: #fef3c7; color: #92400e; padding: 1px 6px; border-radius: 3px;">⛰️ 土 EARTH</span>
      </div>

      <div style="background: #ffedd5; border: 1.5px solid #ea580c; border-radius: 4px; padding: 2px 16px; font-size: 11px; font-weight: 800; color: #9a3412; letter-spacing: 1px; display: flex; align-items: center; gap: 4px; margin-top: 3px;">
        <span>🔥</span> DESIRE
      </div>
    </div>

  </div>
</div>
"""
    return html

# ==========================================
# GROUNDED PROMPT BUILDER FOR NATAL QI MEN
# ==========================================

def build_grounded_qimen_destiny_prompt(birth_date_str: str, birth_time_str: str, gender: str, question: str) -> Tuple[str, Dict[str, Any], str, str]:
    """
    Computes Four Pillars and Natal Qi Men chart, generating both
    the visual Joey Yap HTML chart and the Component Matrix Markdown table.
    Returns: (prompt, chart_data, chart_html, matrix_md)
    """
    year, month, day, hour, minute = parse_date_and_time(birth_date_str, birth_time_str)
    
    if year and month and day:
        pillars = calculate_four_pillars(year, month, day, hour, minute)
    else:
        # Fallback reference pillars (1990-05-15 09:30)
        pillars = calculate_four_pillars(1990, 5, 15, 9, 30)

    # Calculate Qi Men chart using authentic Zhi Run Fa (置閏法)
    d_stem_name = pillars['day']['stem_name']
    d_branch_name = pillars['day']['branch_name']
    d_stem_idx = STEM_NAMES.index(d_stem_name) if d_stem_name in STEM_NAMES else 0
    d_branch_idx = BRANCH_NAMES.index(d_branch_name) if d_branch_name in BRANCH_NAMES else 0
    dun_type, ju_num, term_name = get_qimen_dun_and_ju(year or 1990, month or 5, day or 15, d_stem_idx, d_branch_idx)

    chart_data = calculate_qimen_chart_from_pillars(pillars, dun_type=dun_type, ju_num=ju_num)
    matrix_md = generate_component_matrix_markdown(chart_data)
    chart_html = generate_qimen_chart_html(chart_data, title="NATAL QIMEN DESTINY CHART")

    destiny_p = chart_data['destiny_palace']
    p_info = chart_data['palaces'][destiny_p]

    prompt = (
        f"Natal Qi Men Destiny Consultation Request:\n"
        f"- Birth Date: {birth_date_str} (Solar: {year}-{month:02d}-{day:02d})\n"
        f"- Birth Time: {birth_time_str} (Solar Hour: {hour:02d}:{minute:02d})\n"
        f"- Gender: {gender}\n"
        f"- Inquiry / Focus: {question}\n\n"
        f"MANDATORY CALCULATED QI MEN CHART DATA ({chart_data['structure_desc']}):\n"
        f"- Destiny Palace (命宫): {PALACES_INFO[destiny_p]['name']} ({destiny_p}) {PALACES_INFO[destiny_p]['trigram']} {PALACES_INFO[destiny_p]['element']}\n"
        f"- Guardian Deity (本命八神): {p_info['deity_full']}\n"
        f"- Life Star (本命九星): {p_info['star_full']}\n"
        f"- Life Door (本命八門): {p_info['door_full']}\n"
        f"- Heavenly Stem: {p_info['heaven_stem']['char']} ({p_info['heaven_stem']['pinyin']})\n\n"
        f"MANDATORY FORMATTING REQUIREMENT:\n"
        f"Your response MUST include this exact section and table as Section 2:\n\n"
        f"{matrix_md}\n\n"
        f"STRICT CONSULTATION INSTRUCTIONS:\n"
        f"1. Follow the authentic Natal Qi Men Destiny Reading framework.\n"
        f"2. Decode the client's Destiny Palace, Guardian Deity capabilities, and spiritual archetype.\n"
        f"3. Evaluate the 8 Life Aspects across the palaces (Destiny, Wealth, Career, Relationships, Health, Knowledge, Subconscious, Karmic).\n"
        f"4. Provide concrete, non-superstitious strategic action steps for personal mastery."
    )

    return prompt, chart_data, chart_html, matrix_md
