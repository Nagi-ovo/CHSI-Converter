import json
from pathlib import Path

import pytest

UNIVERSITY_NAMES = json.loads(
    (Path(__file__).parents[1] / "data" / "university_names.json").read_text(encoding="utf-8")
)


def test_historical_institution_names_remain_available():
    historical_names = {
        "佛山科学技术学院",
        "信阳师范学院",
        "内蒙古科技大学包头师范学院",
        "华北科技学院",
        "南昌工程学院",
        "合肥学院",
        "吉林化工学院",
        "嘉兴学院",
        "天水师范学院",
        "宁夏师范学院",
        "安徽科技学院",
        "常熟理工学院",
        "榆林学院",
        "浙江科技学院",
        "淮阴工学院",
        "湖南理工学院",
        "湖州师范学院",
        "滨州学院",
        "福建工程学院",
        "绍兴文理学院",
        "西藏农牧学院",
        "赤峰学院",
        "重庆三峡学院",
        "重庆科技学院",
        "闽江学院",
        "防灾科技学院",
    }
    assert historical_names <= UNIVERSITY_NAMES.keys()


@pytest.mark.parametrize(
    ("chinese_name", "english_name"),
    [
        ("南昌科技职业大学", "Nanchang Vocational University of Science and Technology"),
        ("桂林师范学院", "Guilin Normal University"),
        ("广西师范大学", "Guangxi Normal University"),
        ("内蒙古科技大学", "Inner Mongolia University of Science and Technology"),
        ("北华大学", "Beihua University"),
        ("南昌航空大学", "Nanchang Hangkong University"),
    ],
)
def test_institution_names_do_not_regress(chinese_name, english_name):
    assert UNIVERSITY_NAMES[chinese_name] == english_name
