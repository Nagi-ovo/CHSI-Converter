# University name dictionary

`university_names.json` contains 3,053 exact Chinese → English mappings, including historical institution names that can still appear on older reports.

## Sources and attribution

The original 582 mappings were derived from [xioajiumi/Chinese_Universities](https://github.com/xioajiumi/Chinese_Universities), commit `e088fddc329a6f0148ca72fd3b4d0fe069f13e3a`, CSV fields `name` and `name_eng`. That source describes its data as the 2021 ShanghaiRanking university list. Retrieved 2026-10-13; its MIT copyright and license notice are retained in [LICENSE](LICENSE).

[PR #25](https://github.com/Nagi-ovo/CHSI-Converter/pull/25) contributed 2,471 additional Chinese-name keys. The contributor reports using the Ministry of Education's 2026 institution list and Baidu for the expanded data. This attribution records the contributor's stated sources; the Ministry's Chinese-name list does not verify the English translations. The expanded English names are community reference data and have not all been independently checked against school websites.

The 26 historical keys omitted by the expansion were restored. The contributor's updates to existing entries are retained apart from the specific corrections below. Adding a current institution name must not remove its historical name or silently substitute one institution for another.

## Usage and corrections

This is not a complete national register or a certification of every English name. Check the institution's official English website or charter before using a name in an application or other formal document; the converter permits a manual English-name override. Unknown names remain unchanged and require user input. Do not use fuzzy matching or automatic translation to infer an institution's identity.

Corrections should record the exact Chinese name, the official English wording, the source URL, and the date checked. Original word spacing was restored for 北华大学 → Beihua University and 南昌航空大学 → Nanchang Hangkong University.

## Checked entries

- 北京工业大学 → Beijing University of Technology: [official introduction](https://english.bjut.edu.cn/About/About_BJUT.htm), checked 2026-10-13.
- 南昌科技职业大学 → Nanchang Vocational University of Science and Technology: [school charter, Article 2](https://www.thdm.edu.cn/h-col-182.html), checked 2026-10-25.
- 桂林师范学院 → Guilin Normal University: [school's published name statement](https://ghw.glnc.edu.cn/info/1034/1077.htm), checked 2026-10-25. This is a different institution from 广西师范大学 (Guangxi Normal University).
- 内蒙古科技大学 → Inner Mongolia University of Science and Technology: [official international admission instructions](https://dice.imust.edu.cn/info/1150/2121.htm), checked 2026-10-25.
