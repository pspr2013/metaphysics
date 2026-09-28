import datetime
import re
from typing import Dict, Any, Optional, List, Tuple

STEM_NAMES = ['Jia', 'Yi', 'Bing', 'Ding', 'Wu', 'Ji', 'Geng', 'Xin', 'Ren', 'Gui']
STEM_CHARS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
STEM_ELEMENTS = [
    'Yang Wood', 'Yin Wood', 
    'Yang Fire', 'Yin Fire', 
    'Yang Earth', 'Yin Earth', 
    'Yang Metal', 'Yin Metal', 
    'Yang Water', 'Yin Water'
]
STEM_SHORT_ELEMENTS = [
    'Wood', 'Wood', 'Fire', 'Fire', 'Earth', 'Earth', 'Metal', 'Metal', 'Water', 'Water'
]

BRANCH_NAMES = ['Zi', 'Chou', 'Yin', 'Mao', 'Chen', 'Si', 'Wu', 'Wei', 'Shen', 'You', 'Xu', 'Hai']
BRANCH_CHARS = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
BRANCH_ANIMALS = [
    'Rat 鼠', 'Ox 牛', 'Tiger 虎', 'Rabbit 兔', 'Dragon 龍', 'Snake 蛇',
    'Horse 馬', 'Goat 羊', 'Monkey 猴', 'Rooster 雞', 'Dog 狗', 'Pig 豬'
]
BRANCH_ELEMENTS = [
    '水 Yang Water', '± Yin Earth', '木 Yang Wood', '木 Yin Wood', '± Yang Earth', '火 Yin Fire',
    '火 Yang Fire', '± Yin Earth', '金 Yang Metal', '金 Yin Metal', '± Yang Earth', '水 Yin Water'
]

# Hidden Stems mapping in classical order (matching standard Joey Yap Natal Chart ephemeris)
BRANCH_HIDDEN_STEMS_MAP = {
    0: [{'char': '癸', 'name': 'Gui', 'polarity_elem': '-Water水', 'stem_idx': 9}], # Zi
    1: [
        {'char': '癸', 'name': 'Gui', 'polarity_elem': '-Water水', 'stem_idx': 9},
        {'char': '辛', 'name': 'Xin', 'polarity_elem': '-Metal金', 'stem_idx': 7},
        {'char': '己', 'name': 'Ji', 'polarity_elem': '-Earth土', 'stem_idx': 5}
    ], # Chou
    2: [
        {'char': '戊', 'name': 'Wu', 'polarity_elem': '+Earth土', 'stem_idx': 4},
        {'char': '丙', 'name': 'Bing', 'polarity_elem': '+Fire火', 'stem_idx': 2},
        {'char': '甲', 'name': 'Jia', 'polarity_elem': '+Wood木', 'stem_idx': 0}
    ], # Yin
    3: [{'char': '乙', 'name': 'Yi', 'polarity_elem': '-Wood木', 'stem_idx': 1}], # Mao
    4: [
        {'char': '乙', 'name': 'Yi', 'polarity_elem': '-Wood木', 'stem_idx': 1},
        {'char': '癸', 'name': 'Gui', 'polarity_elem': '-Water水', 'stem_idx': 9},
        {'char': '戊', 'name': 'Wu', 'polarity_elem': '+Earth土', 'stem_idx': 4}
    ], # Chen
    5: [
        {'char': '庚', 'name': 'Geng', 'polarity_elem': '+Metal金', 'stem_idx': 6},
        {'char': '丙', 'name': 'Bing', 'polarity_elem': '+Fire火', 'stem_idx': 2},
        {'char': '戊', 'name': 'Wu', 'polarity_elem': '+Earth土', 'stem_idx': 4}
    ], # Si
    6: [
        {'char': '己', 'name': 'Ji', 'polarity_elem': '-Earth土', 'stem_idx': 5},
        {'char': '丁', 'name': 'Ding', 'polarity_elem': '-Fire火', 'stem_idx': 3}
    ], # Wu
    7: [
        {'char': '丁', 'name': 'Ding', 'polarity_elem': '-Fire火', 'stem_idx': 3},
        {'char': '己', 'name': 'Ji', 'polarity_elem': '-Earth土', 'stem_idx': 5},
        {'char': '乙', 'name': 'Yi', 'polarity_elem': '-Wood木', 'stem_idx': 1}
    ], # Wei
    8: [
        {'char': '戊', 'name': 'Wu', 'polarity_elem': '+Earth土', 'stem_idx': 4},
        {'char': '壬', 'name': 'Ren', 'polarity_elem': '+Water水', 'stem_idx': 8},
        {'char': '庚', 'name': 'Geng', 'polarity_elem': '+Metal金', 'stem_idx': 6}
    ], # Shen
    9: [{'char': '辛', 'name': 'Xin', 'polarity_elem': '-Metal金', 'stem_idx': 7}], # You
    10: [
        {'char': '辛', 'name': 'Xin', 'polarity_elem': '-Metal金', 'stem_idx': 7},
        {'char': '丁', 'name': 'Ding', 'polarity_elem': '-Fire火', 'stem_idx': 3},
        {'char': '戊', 'name': 'Wu', 'polarity_elem': '+Earth土', 'stem_idx': 4}
    ], # Xu
    11: [
        {'char': '甲', 'name': 'Jia', 'polarity_elem': '+Wood木', 'stem_idx': 0},
        {'char': '壬', 'name': 'Ren', 'polarity_elem': '+Water水', 'stem_idx': 8}
    ] # Hai
}

# Reference Date: 2000-01-01 was Wu Wu (Stem: Wu=4, Branch: Wu=6)
REF_DATE = datetime.date(2000, 1, 1)
REF_STEM_IDX = 4
REF_BRANCH_IDX = 6

def get_10_god(dm_idx: int, target_idx: int) -> Dict[str, str]:
    """
    Computes 10 God notation between Day Master stem and target stem.
    Returns:
      zh_full: e.g. '正財'
      zh_short: e.g. '財'
      code: e.g. 'DW'
      en_full: e.g. 'Direct Wealth'
    """
    dm_elem = dm_idx // 2
    target_elem = target_idx // 2
    same_polar = (dm_idx % 2) == (target_idx % 2)
    
    if dm_elem == target_elem:
        if dm_idx == target_idx:
            return {'zh_full': '日元', 'zh_short': '日', 'code': 'DM', 'en_full': 'Day Master'}
        return {'zh_full': '比肩', 'zh_short': '比', 'code': 'F', 'en_full': 'Friend'} if same_polar else {'zh_full': '劫財', 'zh_short': '劫', 'code': 'RW', 'en_full': 'Rob Wealth'}
    elif (dm_elem + 1) % 5 == target_elem:
        return {'zh_full': '食神', 'zh_short': '食', 'code': 'EG', 'en_full': 'Eating God'} if same_polar else {'zh_full': '傷官', 'zh_short': '傷', 'code': 'HO', 'en_full': 'Hurting Officer'}
    elif (dm_elem + 2) % 5 == target_elem:
        return {'zh_full': '偏財', 'zh_short': '才', 'code': 'IW', 'en_full': 'Indirect Wealth'} if same_polar else {'zh_full': '正財', 'zh_short': '財', 'code': 'DW', 'en_full': 'Direct Wealth'}
    elif (target_elem + 2) % 5 == dm_elem:
        return {'zh_full': '七殺', 'zh_short': '殺', 'code': '7K', 'en_full': 'Seven Killings'} if same_polar else {'zh_full': '正官', 'zh_short': '官', 'code': 'DO', 'en_full': 'Direct Officer'}
    elif (target_elem + 1) % 5 == dm_elem:
        return {'zh_full': '偏印', 'zh_short': '印', 'code': 'IR', 'en_full': 'Indirect Resource'} if same_polar else {'zh_full': '正印', 'zh_short': '印', 'code': 'DR', 'en_full': 'Direct Resource'}
    return {'zh_full': '', 'zh_short': '', 'code': '', 'en_full': ''}

def parse_date_and_time(birth_date_str: str, birth_time_str: Optional[str] = None) -> Tuple[Optional[int], Optional[int], Optional[int], int, int]:
    year, month, day = None, None, None
    
    # Check for Month Name (e.g., '03/Jun/1981', '3 June 1981', 'June 3, 1981')
    m_month_word = re.search(r'([A-Za-z]{3,9})', birth_date_str)
    if m_month_word:
        word = m_month_word.group(1).lower()[:3]
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        if word in months:
            month = months.index(word) + 1
            nums = [int(n) for n in re.findall(r'\d+', birth_date_str)]
            if len(nums) >= 2:
                # One is year (4 digits), other is day
                for n in nums:
                    if n >= 1900:
                        year = n
                    elif 1 <= n <= 31:
                        day = n
    if not (year and month and day):
        # Try ISO YYYY-MM-DD
        m_iso = re.search(r'(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})', birth_date_str)
        if m_iso:
            year, month, day = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
        else:
            # Try MM/DD/YYYY or DD/MM/YYYY
            m_slash = re.search(r'(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})', birth_date_str)
            if m_slash:
                n1, n2, y_val = int(m_slash.group(1)), int(m_slash.group(2)), int(m_slash.group(3))
                year = y_val
                # If first is > 12, it must be DD/MM/YYYY
                if n1 > 12 >= n2:
                    day, month = n1, n2
                elif n2 > 12 >= n1:
                    month, day = n1, n2
                else:
                    # In standard HTML date input, browsers in US use MM/DD/YYYY
                    month, day = n1, n2

    hour, minute = 12, 0
    time_str = birth_time_str or birth_date_str
    if time_str and time_str.lower() != "unknown":
        m_time = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', time_str, re.IGNORECASE)
        if m_time:
            hour = int(m_time.group(1))
            minute = int(m_time.group(2))
            ampm = m_time.group(3)
            if ampm:
                if ampm.lower() == 'pm' and hour < 12:
                    hour += 12
                elif ampm.lower() == 'am' and hour == 12:
                    hour = 0

    return year, month, day, hour, minute

def calculate_four_pillars(year: int, month: int, day: int, hour: int = 12, minute: int = 0) -> Dict[str, Any]:
    dt = datetime.date(year, month, day)

    # 1. Day Pillar
    target_dt = dt
    if hour >= 23:
        target_dt = dt + datetime.timedelta(days=1)
    diff = (target_dt - REF_DATE).days
    day_stem_idx = (REF_STEM_IDX + diff) % 10
    day_branch_idx = (REF_BRANCH_IDX + diff) % 12

    # 2. Hour Pillar
    total_mins = hour * 60 + minute
    if total_mins >= 23 * 60 or total_mins < 1 * 60:
        h_branch_idx = 0  # Zi
    else:
        h_branch_idx = ((total_mins - 60) // 120 + 1) % 12
        
    h_start_stem = {0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8}[day_stem_idx % 5]
    h_stem_idx = (h_start_stem + h_branch_idx) % 10

    # 3. Year Pillar
    y = year
    if (month < 2) or (month == 2 and day < 4):
        y = year - 1
    y_stem_idx = (y - 4) % 10
    y_branch_idx = (y - 4) % 12

    # 4. Month Pillar
    if (month == 1 and day < 6):
        m_branch_idx = 0
    elif (month == 1 and day >= 6) or (month == 2 and day < 4):
        m_branch_idx = 1
    elif (month == 2 and day >= 4) or (month == 3 and day < 6):
        m_branch_idx = 2
    elif (month == 3 and day >= 6) or (month == 4 and day < 5):
        m_branch_idx = 3
    elif (month == 4 and day >= 5) or (month == 5 and day < 6):
        m_branch_idx = 4
    elif (month == 5 and day >= 6) or (month == 6 and day < 6):
        m_branch_idx = 5
    elif (month == 6 and day >= 6) or (month == 7 and day < 7):
        m_branch_idx = 6
    elif (month == 7 and day >= 7) or (month == 8 and day < 8):
        m_branch_idx = 7
    elif (month == 8 and day >= 8) or (month == 9 and day < 8):
        m_branch_idx = 8
    elif (month == 9 and day >= 8) or (month == 10 and day < 8):
        m_branch_idx = 9
    elif (month == 10 and day >= 8) or (month == 11 and day < 7):
        m_branch_idx = 10
    elif (month == 11 and day >= 7) or (month == 12 and day < 7):
        m_branch_idx = 11
    else:
        m_branch_idx = 0

    m_start_stem = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}[y_stem_idx % 5]
    m_offset = (m_branch_idx - 2) % 12
    m_stem_idx = (m_start_stem + m_offset) % 10

    # Build 10 Gods for each stem
    pillars_meta = {
        'hour': {
            'stem_idx': h_stem_idx,
            'branch_idx': h_branch_idx,
            'stem_char': STEM_CHARS[h_stem_idx],
            'stem_name': STEM_NAMES[h_stem_idx],
            'stem_elem': STEM_SHORT_ELEMENTS[h_stem_idx],
            'stem_god': get_10_god(day_stem_idx, h_stem_idx),
            'branch_char': BRANCH_CHARS[h_branch_idx],
            'branch_name': BRANCH_NAMES[h_branch_idx],
            'branch_animal': BRANCH_ANIMALS[h_branch_idx],
            'branch_elem': BRANCH_ELEMENTS[h_branch_idx],
            'hidden_stems': [
                {
                    **hs,
                    'god': get_10_god(day_stem_idx, hs['stem_idx'])
                } for hs in BRANCH_HIDDEN_STEMS_MAP[h_branch_idx]
            ]
        },
        'day': {
            'stem_idx': day_stem_idx,
            'branch_idx': day_branch_idx,
            'stem_char': STEM_CHARS[day_stem_idx],
            'stem_name': STEM_NAMES[day_stem_idx],
            'stem_elem': STEM_SHORT_ELEMENTS[day_stem_idx],
            'stem_god': get_10_god(day_stem_idx, day_stem_idx),
            'branch_char': BRANCH_CHARS[day_branch_idx],
            'branch_name': BRANCH_NAMES[day_branch_idx],
            'branch_animal': BRANCH_ANIMALS[day_branch_idx],
            'branch_elem': BRANCH_ELEMENTS[day_branch_idx],
            'hidden_stems': [
                {
                    **hs,
                    'god': get_10_god(day_stem_idx, hs['stem_idx'])
                } for hs in BRANCH_HIDDEN_STEMS_MAP[day_branch_idx]
            ]
        },
        'month': {
            'stem_idx': m_stem_idx,
            'branch_idx': m_branch_idx,
            'stem_char': STEM_CHARS[m_stem_idx],
            'stem_name': STEM_NAMES[m_stem_idx],
            'stem_elem': STEM_SHORT_ELEMENTS[m_stem_idx],
            'stem_god': get_10_god(day_stem_idx, m_stem_idx),
            'branch_char': BRANCH_CHARS[m_branch_idx],
            'branch_name': BRANCH_NAMES[m_branch_idx],
            'branch_animal': BRANCH_ANIMALS[m_branch_idx],
            'branch_elem': BRANCH_ELEMENTS[m_branch_idx],
            'hidden_stems': [
                {
                    **hs,
                    'god': get_10_god(day_stem_idx, hs['stem_idx'])
                } for hs in BRANCH_HIDDEN_STEMS_MAP[m_branch_idx]
            ]
        },
        'year': {
            'stem_idx': y_stem_idx,
            'branch_idx': y_branch_idx,
            'stem_char': STEM_CHARS[y_stem_idx],
            'stem_name': STEM_NAMES[y_stem_idx],
            'stem_elem': STEM_SHORT_ELEMENTS[y_stem_idx],
            'stem_god': get_10_god(day_stem_idx, y_stem_idx),
            'branch_char': BRANCH_CHARS[y_branch_idx],
            'branch_name': BRANCH_NAMES[y_branch_idx],
            'branch_animal': BRANCH_ANIMALS[y_branch_idx],
            'branch_elem': BRANCH_ELEMENTS[y_branch_idx],
            'hidden_stems': [
                {
                    **hs,
                    'god': get_10_god(day_stem_idx, hs['stem_idx'])
                } for hs in BRANCH_HIDDEN_STEMS_MAP[y_branch_idx]
            ]
        },
        'day_master': STEM_NAMES[day_stem_idx],
        'day_master_element': STEM_ELEMENTS[day_stem_idx],
        'day_animal': BRANCH_ANIMALS[day_branch_idx]
    }
    return pillars_meta

def generate_natal_chart_html(p: Dict[str, Any]) -> str:
    """
    Renders an authentic, classical Joey Yap style Natal Chart (本命八字)
    with Hour (時), Day (日), Month (月), Year (年) ordered from left to right.
    """
    order = ['hour', 'day', 'month', 'year']
    col_titles = {'hour': '時 Hour', 'day': '日 Day', 'month': '月 Month', 'year': '年 Year'}

    html = """
<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 900px; margin: 20px auto; background: #ffffff; border: 2px solid #856404; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); color: #212529; overflow: hidden;">
  <!-- Header Bar -->
  <div style="background: #7a1518; color: #ffffff; padding: 10px 16px; display: flex; justify-content: space-between; align-items: center; font-weight: bold; font-size: 16px; border-bottom: 2px solid #856404;">
    <span>NATAL CHART 本命八字</span>
    <span style="font-size: 13px; font-weight: normal; opacity: 0.9;">Classical Chinese Metaphysics</span>
  </div>

  <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 14px;">
    <!-- Column Headers -->
    <thead>
      <tr style="background: #fdfaf2; color: #856404; border-bottom: 2px solid #d4af37; font-weight: 600;">
"""
    for col in order:
        html += f"""        <th style="padding: 10px 8px; width: 22%; border-right: 1px solid #dcdcdc;">{col_titles[col]}</th>\n"""
    html += """        <th style="padding: 10px 4px; width: 12%; font-size: 12px; color: #6c757d;">Pillar</th>\n      </tr>\n    </thead>\n    <tbody>\n"""

    # ROW 1: Heavenly Stems (天干)
    html += """      <!-- Row 1: Heavenly Stems -->\n      <tr style="border-bottom: 2px solid #d4af37; background: #ffffff;">\n"""
    for col in order:
        meta = p[col]
        god = meta['stem_god']
        html += f"""        <td style="padding: 12px 6px; border-right: 1px solid #e2e8f0; vertical-align: middle;">
          <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
            <div style="border: 1px solid #ced4da; border-radius: 3px; padding: 3px 5px; font-size: 11px; line-height: 1.2; background: #f8f9fa;">
              <div style="font-weight: bold; color: #212529;">{god['zh_full']}</div>
              <div style="color: #6c757d; font-size: 10px;">{god['code']}</div>
            </div>
            <div>
              <div style="font-size: 32px; font-weight: bold; line-height: 1; color: #1a202c;">{meta['stem_char']}</div>
              <div style="font-size: 13px; font-weight: 600; color: #4a5568;">{meta['stem_name']}</div>
              <div style="font-size: 12px; color: #718096;">{meta['stem_elem']}</div>
            </div>
          </div>
        </td>\n"""
    html += """        <td style="padding: 8px; border-left: 2px solid #856404; font-size: 12px; font-weight: bold; color: #856404; background: #fdfaf2; vertical-align: middle; line-height: 1.3;">
          天干<br><span style="font-size: 10px; font-weight: normal; color: #6c757d;">Heavenly<br>Stems</span>
        </td>\n      </tr>\n"""

    # ROW 2: Earthly Branches (地支)
    html += """      <!-- Row 2: Earthly Branches -->\n      <tr style="border-bottom: 2px solid #d4af37; background: #fafafa;">\n"""
    for col in order:
        meta = p[col]
        html += f"""        <td style="padding: 12px 6px; border-right: 1px solid #e2e8f0; vertical-align: middle;">
          <div style="font-size: 32px; font-weight: bold; line-height: 1; color: #1a202c;">{meta['branch_char']}</div>
          <div style="font-size: 13px; font-weight: 600; color: #4a5568;">{meta['branch_name']}</div>
          <div style="font-size: 12px; font-weight: 500; color: #495057;">{meta['branch_animal']}</div>
          <div style="font-size: 11px; color: #6c757d;">{meta['branch_elem']}</div>
        </td>\n"""
    html += """        <td style="padding: 8px; border-left: 2px solid #856404; font-size: 12px; font-weight: bold; color: #856404; background: #fdfaf2; vertical-align: middle; line-height: 1.3;">
          地支<br><span style="font-size: 10px; font-weight: normal; color: #6c757d;">Earthly<br>Branches</span>
        </td>\n      </tr>\n"""

    # ROW 3: Hidden Stems (藏干)
    html += """      <!-- Row 3: Hidden Stems -->\n      <tr style="background: #ffffff;">\n"""
    for col in order:
        meta = p[col]
        hs_list = meta['hidden_stems']
        html += """        <td style="padding: 10px 4px; border-right: 1px solid #e2e8f0; vertical-align: top;">\n"""
        html += """          <div style="display: flex; justify-content: space-around; align-items: flex-start;">\n"""
        for hs in hs_list:
            god = hs['god']
            html += f"""            <div style="padding: 0 4px; text-align: center;">
              <div style="font-size: 20px; font-weight: bold; color: #2d3748;">{hs['char']}</div>
              <div style="font-size: 11px; font-weight: 600; color: #4a5568;">{hs['name']}</div>
              <div style="font-size: 10px; color: #718096;">{hs['polarity_elem']}</div>
              <div style="font-size: 11px; font-weight: bold; color: #856404; margin-top: 2px;">{god['zh_short']} <span style="font-size: 10px; color: #495057;">{god['code']}</span></div>
            </div>\n"""
        html += """          </div>\n        </td>\n"""
    html += """        <td style="padding: 8px; border-left: 2px solid #856404; font-size: 12px; font-weight: bold; color: #856404; background: #fdfaf2; vertical-align: middle; line-height: 1.3;">
          藏干<br><span style="font-size: 10px; font-weight: normal; color: #6c757d;">Hidden<br>Stems</span>
        </td>\n      </tr>\n    </tbody>\n  </table>\n</div>\n"""
    return html

def generate_natal_chart_markdown(p: Dict[str, Any]) -> str:
    """
    Renders the exact Joey Yap standard chart in Markdown table format:
    Columns: Hour (時) | Day (日) | Month (月) | Year (年)
    """
    h, d, m, y = p['hour'], p['day'], p['month'], p['year']
    
    # Hidden stems strings
    def format_hs(hs_list):
        return " / ".join([f"{hs['char']} {hs['name']} ({hs['polarity_elem']}, {hs['god']['zh_short']} {hs['god']['code']})" for hs in hs_list])

    md = (
        "### NATAL CHART 本命八字\n\n"
        "| 時 Hour | 日 Day | 月 Month | 年 Year | Pillar |\n"
        "| :---: | :---: | :---: | :---: | :---: |\n"
        f"| **{h['stem_char']}** {h['stem_name']} ({h['stem_elem']})<br>`[{h['stem_god']['zh_full']} {h['stem_god']['code']}]` | **{d['stem_char']}** {d['stem_name']} ({d['stem_elem']})<br>`[{d['stem_god']['zh_full']} {d['stem_god']['code']}]` | **{m['stem_char']}** {m['stem_name']} ({m['stem_elem']})<br>`[{m['stem_god']['zh_full']} {m['stem_god']['code']}]` | **{y['stem_char']}** {y['stem_name']} ({y['stem_elem']})<br>`[{y['stem_god']['zh_full']} {y['stem_god']['code']}]` | **天干**<br>Heavenly Stems |\n"
        f"| **{h['branch_char']}** {h['branch_name']}<br>{h['branch_animal']}<br>`{h['branch_elem']}` | **{d['branch_char']}** {d['branch_name']}<br>{d['branch_animal']}<br>`{d['branch_elem']}` | **{m['branch_char']}** {m['branch_name']}<br>{m['branch_animal']}<br>`{m['branch_elem']}` | **{y['branch_char']}** {y['branch_name']}<br>{y['branch_animal']}<br>`{y['branch_elem']}` | **地支**<br>Earthly Branches |\n"
        f"| {format_hs(h['hidden_stems'])} | {format_hs(d['hidden_stems'])} | {format_hs(m['hidden_stems'])} | {format_hs(y['hidden_stems'])} | **藏干**<br>Hidden Stems |\n\n"
        f"* **Day Master (日元):** **{d['stem_char']} {d['stem_name']} ({p['day_master_element']})** sitting on **{d['branch_animal']} ({d['branch_name']})**\n"
    )
    return md

def build_grounded_bazi_prompt(birth_date_str: str, birth_time_str: str, gender: str, question: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Computes exact astronomical pillars, formats prompt, and returns (prompt, pillars_dict).
    """
    year, month, day, hour, minute = parse_date_and_time(birth_date_str, birth_time_str)
    
    if year and month and day:
        pillars = calculate_four_pillars(year, month, day, hour, minute)
        h, d, m, y = pillars['hour'], pillars['day'], pillars['month'], pillars['year']
        chart_table_md = generate_natal_chart_markdown(pillars)
        
        prompt = (
            f"BaZi PSPR Consultation Request:\n"
            f"- Birth Date: {birth_date_str} (Parsed Solar: {year}-{month:02d}-{day:02d})\n"
            f"- Birth Time (Local Solar Time): {birth_time_str} (Parsed: {hour:02d}:{minute:02d})\n"
            f"- Gender: {gender}\n"
            f"- Question / Focus: {question}\n\n"
            f"MANDATORY VERIFIED NATAL CHART (Follow Joey Yap Standard format strictly: Hour, Day, Month, Year):\n\n"
            f"{chart_table_md}\n"
            f"STRICT INSTRUCTIONS:\n"
            f"1. You MUST adopt this exact Four Pillars orientation (Hour on left, Day, Month, Year on right).\n"
            f"2. Day Master is strictly **{d['stem_name']} ({pillars['day_master_element']})** sitting on **{d['branch_name']} ({pillars['day_animal']})**.\n"
            f"3. Provide an authentic, comprehensive Phann Sophearith PSPR analysis:\n"
            f"   - Level 1: Day Master Strength & Climate Regulation (Tiao Hou)\n"
            f"   - Level 2: Ten Gods Quality Qualification (Superior, Good, Average, Poor)\n"
            f"   - Level 3: Earthly Branch Dynamics (Combinations, Clashes, Harms, Punishments, Destructions)\n"
            f"   - Level 4: Strategic Life Guidance (Career, Wealth, Spouse Palace, Health, and 10-Year Luck Cycle management)."
        )
        return prompt, pillars
    else:
        fallback_prompt = (
            f"BaZi PSPR Consultation Request:\n"
            f"- Birth Date: {birth_date_str}\n"
            f"- Birth Time: {birth_time_str}\n"
            f"- Gender: {gender}\n"
            f"- Focus: {question}\n"
            f"Please calculate the Four Pillars and provide PSPR analysis."
        )
        return fallback_prompt, None
