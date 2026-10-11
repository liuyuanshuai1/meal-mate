from app.core.response import AppException
from app.models.food import Food


def parse_ingredients(value: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    if len(lines) > 30:
        raise ValueError("食材最多填写 30 行")
    ingredients = []
    for line in lines:
        name, separator, amount = line.replace("｜", "|").partition("|")
        name, amount = name.strip(), amount.strip()
        if not name or len(name) > 64 or (separator and len(amount) > 64):
            raise ValueError("食材格式应为：名称|用量，每行一种")
        ingredients.append({"name": name, "amount": amount})
    return ingredients


def parse_steps(value: str) -> list[str]:
    steps = [line.strip() for line in value.splitlines() if line.strip()]
    if len(steps) > 20 or any(len(step) > 500 for step in steps):
        raise ValueError("做法最多 20 步，每步不超过 500 字")
    return steps


def validate_published_recipe(food: Food) -> None:
    if food.cook_minutes is not None and not 1 <= food.cook_minutes <= 480:
        raise AppException(40001, "预计时间应在 1 到 480 分钟之间")
    if food.recipe_status != "published":
        return
    if not food.cook_minutes or not food.ingredients or not food.recipe_steps:
        raise AppException(40001, "发布做法前请填写食材、预计时间和步骤")
    if any(not isinstance(item, dict) or not item.get("name") for item in food.ingredients):
        raise AppException(40001, "请填写有效的食材名称")
    if any(not isinstance(step, str) or not step.strip() for step in food.recipe_steps):
        raise AppException(40001, "请填写有效的做法步骤")
