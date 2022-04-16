import mysql.connector
cnx = mysql.connector.connect(user='root', password='root', host='127.0.0.1', database='information_schema')
cursorStarter = cnx.cursor()


def creatDatabaseAndTables():  # creates a new database and sets up it's tables
    query = "CREATE DATABASE pa2_albinkarlsson"
    cursorStarter.execute(query)
    cnx = mysql.connector.connect(
        user='root', password='root', host='127.0.0.1', database='pa2_albinkarlsson')
    # since a database hasd to be named before creation i have to make a new contector after it was created
    cursorTemp = cnx.cursor()
    Columns = [("recipeName", "varchar(50)"), ("foodType", "varchar(50)")]
    createTable("recipes", Columns, cursorTemp)

    Columns = [("ingredientName", "varchar(50)")]
    createTable("Ingredients", Columns, cursorTemp)

    createTableRecipieIngredientsLink(cursorTemp)
    createTableStorage(cursorTemp)

    query = "CREATE VIEW recipesICanMake AS SELECT DISTINCT(recipeName), foodType FROM recipes JOIN recipeingredientslink ON recipes.recipeName = recipeingredientslink.recipes WHERE recipeingredientslink.ingredients IN (SELECT ingredients FROM storage WHERE recipeingredientslink.ingredients = storage.ingredients AND recipeingredientslink.amount < storage.amount);"
    cursorTemp.execute(query)
    cnx.commit()


def createTable(tableName, collumns, cursor):  # cretes a databeses tables
    query = "CREATE TABLE " + tableName + " ("
    for collumn in collumns:
        query = query + collumn[0] + " " + collumn[1] + ", "
    query = query + " PRIMARY KEY(" + collumns[0][0] + "))"
    print(query)
    cursor.execute(query)


def createTableRecipieIngredientsLink(cursor):
    query = "CREATE TABLE recipeIngredientsLink (id int, ingredients varchar(50), amount int, recipes varchar(50), PRIMARY KEY(id), FOREIGN KEY(ingredients) REFERENCES ingredients(ingredientName), FOREIGN KEY(recipes) REFERENCES recipes(recipeName))"
    cursor.execute(query)


def createTableStorage(cursor):
    query = "CREATE TABLE storage (id int, ingredients varchar(50), amount int, PRIMARY KEY(id), FOREIGN KEY(ingredients) REFERENCES ingredients(ingredientName))"
    cursor.execute(query)


def recipesOfFood():
    query = "SELECT DISTINCT(foodType), COUNT(foodType) FROM recipes GROUP BY foodType"
    cursor.execute(query)
    foodTypes = cursor.fetchall()
    listFoodTypes = []
    x = 0
    while x < len(foodTypes):
        print("There are " + str(foodTypes[x][1]) + " recipes of type " + str(foodTypes[x][0]))
        listFoodTypes.append(foodTypes[x][0])
        x = x + 1
    choice = input("What food type do you want listed: ")
    typeExists = False
    while typeExists == False:
        if choice in listFoodTypes:
            typeExists = True
        if typeExists == False:
            print("Could not find anything try again")
            choice = input("What food type do you want listed: ")
    query = "SELECT recipeName FROM recipes WHERE foodType = %s"
    cursor.execute(query, (choice,))
    recipes = cursor.fetchall()
    for (recepie,) in recipes:
        print("Recipe: " + recepie)
    puase()


def whatRecipeInclude():
    query = "SELECT * FROM ingredients"
    cursor.execute(query)
    ingredients = cursor.fetchall()
    stringIngredients = ""
    listIngredients = []
    for (ingredient,) in ingredients:
        stringIngredients = stringIngredients + " " + ingredient
        listIngredients.append(ingredient)
    print(stringIngredients)
    query = "SELECT recipeName FROM recipes JOIN recipeingredientslink ON recipeingredientslink.recipes = recipes.recipeName WHERE recipeingredientslink.ingredients = %s"
    ingredient = input ("What ingredient do you want to use: ")
    ingredientFound = False
    while ingredientFound == False:
        if ingredient in listIngredients:
            ingredientFound = True
        if ingredientFound == False:
            print("ingredient could not be found")
            ingredient = input("What ingredient do you want to use: ")

    cursor.execute(query, (ingredient,))
    recipesContaing = cursor.fetchall()
    stringRecipes = ""
    for (recipe,) in recipesContaing:
        stringRecipes = stringRecipes + " " + recipe
    print(stringRecipes)
    puase()


def recipesICanMake():
    query = ("SELECT * FROM recipesICanMake")
    cursor.execute(query)
    posibleMeals = cursor.fetchall()
    if posibleMeals != None:
        print("The options are:")
        for meal in posibleMeals:
            print("Recipe: " + meal[0] + " which is a " + meal[1])
    else:
        print("There are no recipes with can be made out of the currently held ingredients")
    puase()


def whatAmIMissing():
    query = "SELECT recipeName FROM recipes"
    cursor.execute(query)
    recipes = cursor.fetchall()
    print(recipes)
    recipeExists = False
    recipeName = input("What recipe to check ")
    while recipeExists == False:
        for recipe in recipes:
            if recipe[0] == recipeName:
                recipeExists = True
        if recipeExists == False:
            print("Recipe could not be found")
            recipeName = input("What recipe to check ")
    query = "SELECT recipeingredientslink.ingredients, (recipeingredientslink.amount - storage.amount) FROM recipeingredientslink, storage WHERE recipes = %s AND storage.ingredients = recipeingredientslink.ingredients AND storage.ingredients = recipeingredientslink.ingredients AND recipeingredientslink.amount > (SELECT amount FROM storage WHERE ingredients = recipeingredientslink.ingredients);"
    cursor.execute(query, (recipeName,))
    missingIngredients = cursor.fetchall()
    if missingIngredients != None:
        for ingredient in missingIngredients:
            print("Missing " + str(ingredient[1]) + " amount of ingredient " + ingredient[0])
    else:
        print("No ingredient is missing to make " + recipeName)
    puase()


def whatRecipeDoNotUse():
    query = "SELECT * FROM ingredients"
    cursor.execute(query)
    ingredients = cursor.fetchall()
    stringIngredients = ""
    listIngredeints = []
    for (ingredient,) in ingredients:
        stringIngredients = stringIngredients + " " + ingredient
        listIngredeints.append(ingredient)

    print(stringIngredients)
    query = "SELECT recipeName FROM recipes WHERE recipeName NOT IN (SELECT recipes FROM recipeingredientslink WHERE recipeingredientslink.recipes = recipes.recipeName AND recipeingredientslink.ingredients != %s);"
    ingredient = input ("What ingredient do you want to avoid: ")
    
    ingredientFound = False
    while ingredientFound:
        if ingredient in listIngredeints:
            ingredientFound = True
        if ingredient == False:
            print("ingredient could not be found")
            ingredient = input ("What ingredient do you want to use: ")

    cursor.execute(query, (ingredient,))
    recipesNotContaing = cursor.fetchall()
    print(len(recipesNotContaing))
    listGoodRecipes = []
    for recipe in recipesNotContaing:
        listGoodRecipes.append(recipe)
    if len(listGoodRecipes) != 0:
        print("Recipes not using " + ingredient + " are " + str(listGoodRecipes))
    else:
        print("No recipes without " + ingredient + " could be found")
    puase()


def puase():
    stopper = input("")
    x = 0
    while x < 20:
        print("")
        x += 1


# main
cursorStarter.execute("SHOW DATABASES")
databases = cursorStarter.fetchall()
databaseExists = False
for x in databases:
    if "pa2_albinkarlsson" == str(x[0]):
        databaseExists = True

if databaseExists == False:
    creatDatabaseAndTables()
cursorStarter.close()
cnx.close()

cnx = mysql.connector.connect(user='root', password='root', host='127.0.0.1', database='pa2_albinkarlsson')
cursor = cnx.cursor()
userInput = "starter"
while userInput != "":
    print("1 to check what you have the requriments to cook")
    print("2 to check what needs to be bought to make a specific dish")
    print("3 for every recipe containing specific ingredint")
    print("4 for every recipe of type")
    print("5 for every recipe that does not use specific ingredient")
    userInput = input("")
    if userInput == "1":
        recipesICanMake()
    elif userInput == "2":
        whatAmIMissing()
    elif userInput == "3":
        whatRecipeInclude()
    elif userInput == "4":
        recipesOfFood()
    elif userInput == "5":
        whatRecipeDoNotUse()

cursor.close()
cnx.commit()
cnx.close()