---
name: ten-thousand-year-calendar
description: Comprehensive Chinese Metaphysics ephemeris, calendar conversion, and calculation engine based on Phann Sophearith's The Ten Thousand Year Calendar. Use when the user requests BaZi chart plotting, Day Master derivation, Five Tigers/Five Rats formula calculation, Luck Pillar age limit derivation, Solar Terms (Jie Qi) transitions, 60 Jia Zi Na Yin, Ten Gods interactions, Zi Wei Dou Shu palace and star allocations, 24 Mountains bearings, San Yuan 9 Periods, Ba Zhai Life Gua and 8 Wandering Stars, Xuan Kong Flying Star charts, Purple White stars, or San He Water methods.
---

# Ten Thousand Year Calendar Reference and Calculation Engine

A definitive calculation and interpretation engine for Chinese Metaphysics, derived from Phann Sophearith's "The Ten Thousand Year Calendar" (Mastery Academy of Chinese Metaphysics). This skill provides exact calculation algorithms, interaction hierarchies, reference citations, and conflict-resolution rules for BaZi, Zi Wei Dou Shu, and classical Feng Shui.

## When to Use

Activate this skill whenever handling queries concerning:

- BaZi (Four Pillars of Destiny) chart plotting, Day Master derivation, and pillar calculation.
- Five Tigers Chasing Month (Wu Hu Dun Yue) and Five Rats Chasing Hour (Wu Shu Dun Shi) calculations.
- Early Rat (Zi Chu) vs. Late Rat (Ye Zi) hour boundary determination.
- Luck Pillars (Da Yun) sequence direction and age limit point calculation.
- Ten Gods (Shi Shen) classification, hidden stems (Cang Gan), and 12 Growth Phases.
- Earthly Branch interactions: Combinations, Clashes, Punishments, Harms, and Destructions.
- Auxiliary Stars (Shen Sha) and Child Obstruction Sha (Xiao Er Guan Sha).
- Zi Wei Dou Shu chart generation: Life Palace, Body Palace, 5 Elements Bureau, and star streams.
- San Yuan (3 Cycles and 9 Periods) timeline and 24 Mountains Luo Pan compass bearings.
- Ba Zhai (Eight Mansions) Life Gua calculation and 8 Wandering Stars directional placement.
- Xuan Kong Flying Star chart generation, timeliness assessment, and Purple White Script (Zi Bai).
- San He Four Major Water Structures and Water Dragon exits from Di Li Wu Jue.

---

## 1. Temporal Calibration and Calendar Disambiguation

Always execute temporal calibration before performing any calculation:

1. **System Calendar Distinction**:
   - **Solar Calendar (Xia Li / Jie Qi)**: Used strictly for BaZi, Solar Feng Shui, Annual Flying Stars, and 24 Mountains.
   - **Lunar Calendar (Yin Li)**: Used strictly for Zi Wei Dou Shu, traditional festival dates, and lunar day counts.

2. **Astrological Year Boundary (Li Chun)**:
   - The astrological year begins precisely at the minute of **Li Chun (立春, Coming of Spring)**, around February 4.
   - A birth occurring on February 3 or before the exact time of Li Chun belongs to the **preceding solar year**.

3. **Solar Month Boundary (Jie 節)**:
   - Solar months begin at the exact minute of the monthly **Jie (節, Solar Node)**, not the Gregorian 1st of the month nor the Lunar 1st (Chu Yi).

4. **Rat Hour Disambiguation (23:00 - 00:59)**:
   - **Late Rat Hour (Ye Zi 夜子時, 23:00 - 23:59)**: The calendar Day Master remains the current day's stem; the hour stem is taken from the Late Rat column (advancing the stem cycle by one day).
   - **Early Rat Hour (Zi Chu 早子時, 00:00 - 00:59)**: The calendar Day Master is the new day; standard Five Rats formula applies.

---

## 2. BaZi Calculation Engine

### 2.1. Four Pillars Generation Workflow

1. **Year Pillar**:
   - Find the Gregorian birth year in the Ten Thousand Year Calendar.
   - Check if birth is before Li Chun. If before, use the preceding year's 60 Jia Zi.

2. **Month Pillar (Five Tigers Chasing Month)**:
   - Identify the Solar Month Branch based on the 24 Solar Terms (Yin = 1st month, Mao = 2nd, etc.).
   - Use the Year Stem to determine the starting stem for Yin (寅) month:
     - Jia (甲) / Ji (己) Year: 1st month is Bing Yin (丙寅).
     - Yi (乙) / Geng (庚) Year: 1st month is Wu Yin (戊寅).
     - Bing (丙) / Xin (辛) Year: 1st month is Geng Yin (庚寅).
     - Ding (丁) / Ren (壬) Year: 1st month is Ren Yin (壬寅).
     - Wu (戊) / Gui (癸) Year: 1st month is Jia Yin (甲寅).
   - Advance sequentially through the branches to reach the birth month.

3. **Day Pillar**:
   - Extract the 60 Jia Zi day pillar directly from the calendar ephemeris for the given date.
   - The Heavenly Stem is the **Day Master (日主)**.

4. **Hour Pillar (Five Rats Chasing Hour)**:
   - Map birth time to the 12 double-hours: Zi (23:00-00:59), Chou (01:00-02:59), Yin (03:00-04:59), Mao (05:00-06:59), Chen (07:00-08:59), Si (09:00-10:59), Wu (11:00-12:59), Wei (13:00-14:59), Shen (15:00-16:59), You (17:00-18:59), Xu (19:00-20:59), Hai (21:00-22:59).
   - Derive the Rat (Zi) hour stem from the Day Master:
     - Jia (甲) / Ji (己) Day -> Early Rat: Jia Zi (甲子); Late Rat: Bing Zi (丙子).
     - Yi (乙) / Geng (庚) Day -> Early Rat: Bing Zi (丙子); Late Rat: Wu Zi (戊子).
     - Bing (丙) / Xin (辛) Day -> Early Rat: Wu Zi (戊子); Late Rat: Geng Zi (庚子).
     - Ding (丁) / Ren (壬) Day -> Early Rat: Geng Zi (庚子); Late Rat: Ren Zi (壬子).
     - Wu (戊) / Gui (癸) Day -> Early Rat: Ren Zi (壬子); Late Rat: Jia Zi (甲子).

### 2.2. Luck Pillars (Da Yun) and Age Limit Calculation

1. **Direction of Luck Cycle**:
   - **Forward Cycle (順行)**: Yang Male (陽男) or Yin Female (陰女).
   - **Reverse Cycle (逆行)**: Yin Male (陰男) or Yang Female (陽女).

2. **Starting Point**:
   - The first Luck Pillar is the immediate next (forward) or preceding (reverse) pillar relative to the **Month Pillar**.

3. **Age Limit Calculation (起運數)**:
   - **Forward**: Count exact calendar days from birth date forward to the next Solar Node (Jie).
   - **Reverse**: Count exact calendar days from birth date backward to the preceding Solar Node (Jie).
   - Compute starting age: $\text{Age} = \text{round}(\text{Days} / 3)$.
   - Conversion rule: 3 days = 1 year; 1 day = 4 months; 1 hour = 5 days.
   - Subsequent Luck Pillars advance in 10-year blocks (e.g., 8, 18, 28, 38...).

### 2.3. Earthly Branch Interaction Hierarchy

Evaluate interactions using this strict priority order:

1. **Directional Seasonal Combination (San Hui 三會方)**: Highest strength.
   - Yin-Mao-Chen (Spring Wood), Si-Wu-Wei (Summer Fire), Shen-You-Xu (Autumn Metal), Hai-Zi-Chou (Winter Water).
2. **Three Harmony Combination (San He 三合局)**:
   - Shen-Zi-Chen (Water), Hai-Mao-Wei (Wood), Yin-Wu-Xu (Fire), Si-You-Chou (Metal).
3. **Six Combinations (Liu He 六合)**:
   - Zi-Chou (Earth), Yin-Hai (Wood), Mao-Xu (Fire), Chen-You (Metal), Si-Shen (Water), Wu-Wei (Sun/Moon).
4. **Six Clashes (Liu Chong 六沖)**:
   - Zi-Wu, Chou-Wei, Yin-Shen, Mao-You, Chen-Xu, Si-Hai.
5. **Punishments (Xiang Xing 相刑)**:
   - Ungrateful (Yin-Si-Shen), Bullying (Chou-Xu-Wei), Uncivilized (Zi-Mao), Self-Punishment (Chen, Wu, You, Hai).
6. **Six Harms (Liu Hai 六害)**:
   - Zi-Wei, Chou-Wu, Yin-Si, Mao-Chen, Shen-Hai, You-Xu.
7. **Destructions (Xiang Po 相破)**:
   - Zi-You, Chou-Chen, Yin-Hai, Mao-Wu, Si-Shen, Wei-Xu.

---

## 3. Zi Wei Dou Shu Calculation Engine

1. **Establish the 12 Palaces (定十二宮)**:
   - Use the Birth Year Stem to assign Heavenly Stems to the 12 earthly branch sectors starting from Yin (寅) via Five Tigers formula.

2. **Locate Life Palace (Ming Gong) and Body Palace (Shen Gong)**:
   - Life Palace: Starting at Yin (寅), count clockwise to the Birth Lunar Month; from that palace, count counter-clockwise to the Birth Double-Hour.
   - Body Palace: Starting at Yin (寅), count clockwise to the Birth Lunar Month; from that palace, count clockwise to the Birth Double-Hour.
   - 12 Palaces sequence proceeds **counter-clockwise** from Life Palace: Life, Siblings, Marriage, Children, Wealth, Health, Travel, Friends, Career, Property, Fortune, Parents.

3. **Determine Five Elements Bureau (Wu Xing Ju)**:
   - Map the Heavenly Stem and Earthly Branch of the Life Palace to the Bureau: Water 2, Wood 3, Metal 4, Earth 5, or Fire 6.

4. **Allocate Zi Wei (Emperor) and Tian Fu (Sky Treasurer)**:
   - Locate Zi Wei by cross-referencing Lunar Birth Day with the Bureau number.
   - Position Tian Fu opposite Zi Wei across the Yin-Shen diagonal axis (Zi-Chen, Chou-Mao, Yin-Yin, Mao-Chou, etc.).
   - Distribute Northern Stream counter-clockwise from Zi Wei; distribute Southern Stream clockwise from Tian Fu.

5. **Four Transformation Stars (Si Hua)**:
   - Assign Hua Lu, Hua Quan, Hua Ke, and Hua Ji according to the Birth Year Stem table.
   - *Lineage Note*: Note variations across lineages for Geng and Ren stems as documented in Phann Sophearith's text (Part 1, p. 85).

---

## 4. Feng Shui & Spatial Systems Engine

### 4.1. The 24 Mountains Matrix

Each cardinal direction spans 45 degrees, subdivided into three 15-degree Mountains:

- **North (Kan)**: Ren (337.6 - 352.5 deg), Zi (352.6 - 7.5 deg), Gui (7.6 - 22.5 deg).
- **Northeast (Gen)**: Chou (22.6 - 37.5 deg), Gen (37.6 - 52.5 deg), Yin (52.6 - 67.5 deg).
- **East (Zhen)**: Jia (67.6 - 82.5 deg), Mao (82.6 - 97.5 deg), Yi (97.6 - 112.5 deg).
- **Southeast (Xun)**: Chen (112.6 - 127.5 deg), Xun (127.6 - 142.5 deg), Si (142.6 - 157.5 deg).
- **South (Li)**: Bing (157.6 - 172.5 deg), Wu (172.6 - 187.5 deg), Ding (187.6 - 202.5 deg).
- **Southwest (Kun)**: Wei (202.6 - 217.5 deg), Kun (217.6 - 232.5 deg), Shen (232.6 - 247.5 deg).
- **West (Dui)**: Geng (247.6 - 262.5 deg), You (262.6 - 277.5 deg), Xin (277.6 - 292.5 deg).
- **Northwest (Qian)**: Xu (292.6 - 307.5 deg), Qian (307.6 - 322.5 deg), Hai (322.6 - 337.5 deg).

### 4.2. Ba Zhai (Eight Mansions)

1. **Calculate Life Gua**:
   - Male (pre-2000): $(100 - \text{Year Last 2 Digits}) \pmod 9$. (If 5 -> Gua 2 Kun).
   - Male (2000+): $(9 - \text{Year Last 2 Digits}) \pmod 9$ or $(109 - \text{Year}) \pmod 9$. (If 5 -> Gua 2 Kun).
   - Female (pre-2000): $(\text{Year Last 2 Digits} - 4) \pmod 9$. (If 5 -> Gua 8 Gen).
   - Female (2000+): $(\text{Year Last 2 Digits} + 6) \pmod 9$. (If 5 -> Gua 8 Gen).

2. **Group Identification**:
   - **East Four Life**: Gua 1 (Kan), 3 (Zhen), 4 (Xun), 9 (Li).
   - **West Four Life**: Gua 2 (Kun), 6 (Qian), 7 (Dui), 8 (Gen).

3. **Eight Wandering Stars Orientation**:
   - Auspicious: Sheng Qi (Life Generating), Tian Yi (Heavenly Doctor), Yan Nian (Longevity), Fu Wei (Stability).
   - Inauspicious: Huo Hai (Mishaps), Wu Gui (Five Ghosts), Liu Sha (Six Killings), Jue Ming (Life Threatening).

### 4.3. Xuan Kong Flying Stars

1. **Facing vs. Door Direction**:
   - House Facing (facade facing main Yang Qi / road) determines the 9-palace flying star chart.
   - Main Door orientation is evaluated within its respective sector room.

2. **Star Chart Components**:
   - Base Star (Time Star) at bottom-center.
   - Sitting Star (Mountain Star) at top-left (governs health, relationships, people).
   - Facing Star (Water Star) at top-right (governs wealth, cash flow, career).

3. **Timeliness Principle**:
   - Benefic vs. malefic nature is governed strictly by current Period timeliness. Current Period (2024-2043) is **Period 9 (Li Fire)**. Star 9 is Prompt/Current Wang Qi; Star 1 is Sheng Qi; Star 8 is retreating Qi.

### 4.4. San He Water Structures and Di Li Wu Jue

- **Fire Structure (火局乙龍)**: Growth at Yin, Peak at Wu, Exit at Xu (戌 Storage).
- **Water Structure (水局辛龍)**: Growth at Shen, Peak at Zi, Exit at Chen (辰 Storage).
- **Metal Structure (金局丁龍)**: Growth at Si, Peak at You, Exit at Chou (丑 Storage).
- **Wood Structure (木局癸龍)**: Growth at Hai, Peak at Mao, Exit at Wei (未 Storage).
- Drainage exit degrees must be measured using the San He Heaven Plate (Water Ring).

---

## 5. Source Reference Protocol

When delivering calculations or technical analyses, cite the definitive reference source:

- Essentials & Solar Terms: *Phann Sophearith, The Ten Thousand Year Calendar, Section A, pp. 2-4*.
- BaZi Pillars & Five Tigers/Rats: *Phann Sophearith, Section B.13 & B.21, pp. 20-21, 44-60*.
- Hidden Stems (Cang Gan): *Phann Sophearith, Section B.1.6, p. 9*.
- Earthly Branch Interactions: *Phann Sophearith, Section B.2-B.12, pp. 10-19*.
- Ten Gods & Cycles: *Phann Sophearith, Section B.17, pp. 25-27*.
- Auxiliary Stars (Shen Sha): *Phann Sophearith, Section B.19, pp. 29-37*.
- Zi Wei Dou Shu Formulations: *Phann Sophearith, Section C, pp. 62-96*.
- Ba Zhai & 24 Mountains: *Phann Sophearith, Section E.1-E.5, pp. 106-114*.
- Xuan Kong Flying Stars: *Phann Sophearith, Section E.6, pp. 115-141*.
- San He Water Methods: *Phann Sophearith, Section E.7-E.8, pp. 142-146*.

---

## 6. Conflict Handling and Edge Cases

- **Solar vs. Lunar Conflict**: If a user asks for a BaZi chart using the Lunar birthday, convert to the Solar Calendar using the Ten Thousand Year Calendar ephemeris before deriving stems and branches.
- **Li Chun Boundary Conflict**: For births between February 3 and February 5, check the exact minute of solar transit. Never default to February 4 midnight.
- **Rat Hour Midnight Controversy**: When birth is between 23:00 and 23:59, apply the Late Rat (Ye Zi) formula: keep the calendar day's Day Master, advance the hour stem using the Late Rat table.
- **Flying Star Period Conflict**: If a house was constructed in Period 7 (1984-2003) but major roof renovation or occupancy change occurred in Period 8 or 9, explain both the original construction chart and the possibility of a period shift based on occupant transition.
- **Zi Wei Si Hua Lineage Variants**: State the primary transformation according to Phann Sophearith's table, while noting the classical Geng/Ren alternative traditions when relevant.

---

## 7. Quality-Control Verification Checklist

Before finalizing any astrological or spatial chart output:

- [ ] Has the Gregorian birth date been verified against the exact Solar Term (Jie Qi) transition time?
- [ ] For January/early February dates, was the Year Pillar assigned based on Li Chun rather than the Gregorian year?
- [ ] Was the Month Pillar stem derived strictly from the Year Stem via Five Tigers Chasing Month?
- [ ] Was the Hour Pillar stem verified against the Day Master via Five Rats Chasing Hour, accounting for Early vs. Late Rat?
- [ ] In Luck Pillar calculations, was the forward/reverse cycle correctly selected based on gender and Year Stem polarity?
- [ ] Was the Age Limit calculation rounded accurately ($days / 3$)?
- [ ] In Eight Mansions, was the 5-Gua substitution rule applied (Male -> Kun 2, Female -> Gen 8)?
- [ ] In Flying Stars, was House Facing clearly separated from Main Door Facing?
- [ ] Are all factual and formulaic references grounded in Phann Sophearith's *The Ten Thousand Year Calendar*?
