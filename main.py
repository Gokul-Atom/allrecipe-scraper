from requests import get
from bs4 import BeautifulSoup as bs
import os

recipe_site_url = "https://www.allrecipes.com/recipes-a-z-6735880"
response = get(recipe_site_url).text
soup = bs(response, "html.parser")
soups = soup.find_all(class_="link-list__item", attrs="href")
all_categories = [s.find("a").get("href") for s in soups][1:2]
all_categories_name = [s.find("a").text.strip() for s in soups][1:]

if not os.path.exists("all_recipes"):
    os.mkdir("all_recipes")

for category, name in zip(all_categories, all_categories_name):
    print(f"Category: {name}")
    response = get(category).text
    soup = bs(response, "html.parser")
    soups = soup.find(class_="fixedContent").find_all(class_="mntl-card-list-items")
    links = [s.get("href") for s in soups if "/recipe/" in s.get("href")]

    for link in links:
        prep_time, cook_time, total_time, servings, yield_ = "", "", "", "", ""
        response = get(link).text
        soup = bs(response, "html.parser")
        heading = soup.find(class_="article-heading").text.strip()
        print(f"Recipe: {heading}")
        description = soup.find(class_="article-subheading").text.strip()
        recipe_by = soup.find(class_="mntl-attribution__item-name").text.strip()
        for div in soup.find_all(class_="mntl-recipe-details__item"):
            if div.find_all("div")[0].text == "Prep Time:":
                prep_time = div.find_all("div")[1].text
            elif div.find_all("div")[0].text == "Cook Time:":
                cook_time = div.find_all("div")[1].text
            elif div.find_all("div")[0].text == "Total Time:":
                total_time = div.find_all("div")[1].text
            elif div.find_all("div")[0].text == "Servings:":
                servings = div.find_all("div")[1].text
            elif div.find_all("div")[0].text == "Yield:":
                yield_ = div.find_all("div")[1].text
        ingredients = [item.text.strip() for item in soup.find_all(class_="mntl-structured-ingredients__list-item")]
        directions = [item.text.strip() for item in soup.find(class_="comp recipe__steps-content mntl-sc-page mntl-block").find_all(class_="mntl-sc-block-html")]
        serving_per_recipe = soup.find(class_="mntl-nutrition-facts-label__servings").find_all("span")[-1].text
        calories_per_serving = soup.find(class_="mntl-nutrition-facts-label__calories").find_all("span")[-1].text
        nutrition_fact_body = soup.find(class_="mntl-nutrition-facts-label__table-body type--cat").find_all("tr")
        nutrition_fact_rows = [row.text.strip() for row in nutrition_fact_body]
        data = ""
        grams = ""
        percents = ""
        for cell in nutrition_fact_rows[1:]:
            percents += cell.split("\n\n\n")[1] + "|" if len(cell.split("\n\n\n")) > 1 else "|"
            data += cell.split("\n\n\n")[0].split("\n")[0] + "|"
            grams += cell.split("\n\n\n")[0].split("\n")[1] + "|"

        if not os.path.exists(f"all_recipes/{name}.csv"):
            with open(f"all_recipes/{name}.csv", "w") as file:
                file.write(
                    f"recipe_name|description|recipe_by|preparation_time|cook_time|total_time|servings|yield|ingredients|directions|serving_per_recipe|calories_per_serving|{data.lower()}{data.lower().replace('|', '%dv|')}\n")

        with open(f"all_recipes/{name}.csv", "a", encoding="utf-8") as file:
            file.write(
                f"{heading}|{description}|{recipe_by}|{prep_time}|{cook_time}|{total_time}|{servings}|{yield_}|{ingredients}|{directions}|{serving_per_recipe}|{calories_per_serving}|{grams}{percents}\n")
