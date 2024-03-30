"""
main app
"""

from fractions import Fraction
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .fentch import get_teams_and_chals, fraction_score

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")


templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    """
    返回积分表页面
    """
    teams, chals = await get_teams_and_chals()
    result: dict[str, Fraction] = fraction_score(teams, chals)
    return templates.TemplateResponse(
        request=request, name="scoreboard.html", context={"result": result}
    )
