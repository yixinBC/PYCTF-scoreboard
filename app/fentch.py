"""
fentch data from platform
"""

from fractions import Fraction
from httpx import AsyncClient

PLATFORM_URL: str = ""  # 平台URL，结尾不要有/
GAME_ID: int = 0  # 比赛ID
TOKEN: str = ""  # Token


async def get_teams_and_chals() -> tuple[list[str], dict[str, list[str]]]:
    """
    teams:  队伍id的list
    chals:  每个题目名与解出的队伍id关系的dict
            键为题目名，值为解出的队伍id的list
            队伍id从前往后是解出题的顺序
    有空再优化
    """
    async with AsyncClient() as client:
        # 队伍id和队伍名的对应关系
        teams_id_name = {
            i["name"]: i["id"]
            for i in (
                await client.get(f"{PLATFORM_URL}/api/game/{GAME_ID}/scoreboard")
            ).json()["items"]
        }
        teams = [str(i) for i in teams_id_name.values()]
        chals = {}
        cookies = {
            "GZCTF_Token": TOKEN,
        }
        # 获取所有提交，需要Monitor权限
        submissions = (
            await client.get(
                f"{PLATFORM_URL}/api/game/{GAME_ID}/submissions?type=Accepted&count=50000",
                cookies=cookies,
            )
        ).json()

        # 获取所有提交，需要User权限
        challenge_details = (
            await client.get(
                f"{PLATFORM_URL}/api/game/{GAME_ID}/details", cookies=cookies
            )
        ).json()

        for challenge_name in [
            i["title"] for i in challenge_details["challenges"]["Misc"]
        ]:
            chals.update({challenge_name: []})
            for submission in submissions[::-1]:
                if submission["challenge"] == challenge_name:
                    chals[challenge_name].append(str(teams_id_name[submission["team"]]))
    return teams, chals


async def get_id_with_name() -> dict[str, str]:
    """
    获取当前Game下的队伍id和队伍名的对应关系
    """
    async with AsyncClient() as client:
        # 队伍id和队伍名的对应关系
        return {
            i["name"]: i["id"]
            for i in (
                await client.get(f"{PLATFORM_URL}/api/game/{GAME_ID}/scoreboard")
            ).json()["items"]
        }


def fraction_score(
    teams: list[str], chals: dict[str, list[str]]
) -> dict[str, Fraction]:
    # 分别创建队伍得分字典和失败队伍（未拿到自己题目一血）列表
    res: dict[str, Fraction] = {_: Fraction(0) for _ in teams}
    fail = []
    for c, t in chals.items():
        # 题目为0解的情况下跳过
        if len(t) == 0:
            continue
        # 题目一血不是对应队伍，该队伍加入失败列表
        elif c.split("_")[0] != t[0]:
            fail.append(c.split("_")[0])
        # 题目一血是对应队伍，每个队平分本题分数
        else:
            for _ in t:
                # 有一些非预期行为，等等修改
                try:
                    res[_] += Fraction(1, len(t))
                except:
                    continue
    # 失败队伍的得分视为0
    for _ in fail:
        res[_] = Fraction(0)
    # 得分字典从高到低排序（同分可能还要按最后成功提交时间来排序，这里就不涉及了）
    # Fraction对象最后输出到排行榜的时候直接str()或者单独print()就会变成分数形式表示
    return dict(sorted((res.items()), key=lambda x: x[1], reverse=True))
