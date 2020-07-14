import requests
import pandas as pd
import sys
import math
import time
pd.options.mode.chained_assignment = None  # default='warn'
api_key = 0
r = requests.get(f"http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key={api_key}&format=json")

games = r.json()["applist"]["apps"]


#store.steampowered.com/appreviews/<appid>?json=1
#https://store.steampowered.com/api/appdetails?appids=<appid>
#(pd.DataFrame.from_dict(games)).to_csv("games_fresh")

#df = pd.DataFrame.from_dict(games)
#dfCopy = df
#testDF = df.tail(10)
df = pd.read_csv("fullSteamV4.csv")



def getReviewInfo(appid):
    r = requests.get(f"http://store.steampowered.com/appreviews/{appid}?json=1")
    try:
        review_info = r.json()["query_summary"]
        del review_info["num_reviews"]
        return review_info
    except:
        return


def getGameInfo(appid):
    game_info = {}
    r = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}")
    success = r.json()[str(appid)]["success"]
    try:
        data = r.json()[str(appid)]["data"]
    except:
        pass

    #Add success
    game_info["success"] = success

    #Add isfree
    try:
        is_free = data["is_free"]
        game_info["is_free"] = is_free
    except:
        pass
    #Add price data
    try:
        price = data["price_overview"]["final_formatted"]
        game_info["price"] = price
    except:
        pass

    #Add release date
    try:
        release_date = data["release_date"]["date"]
        game_info["release_date"] = release_date
    except:
        pass

    #Add genre data
    try:
        genres = []
        for i in data["genres"]:
            genres.append(i["description"])
        genres = ", ".join(genres)
        game_info["genres"] = genres
    except:
        pass

    #Add category data
    try:
        tags = []
        for i in data["categories"]:
            tags.append(i["description"])
        tags = ", ".join(tags)
        game_info["tags"] = tags
    except:
        pass

    #Add developers (IF MULTIPLE, THEN IT IS JOINED BY " & ")
    try:
        developers = data["developers"]
        developers = " & ".join(developers)
        game_info["developers"] = developers
    except:
        pass
    #Add publishers (IF MULTIPLE, THEN IT IS JOINED BY " & ")
    try:
        publishers = data["publishers"]
        publishers = " & ".join(publishers)
        game_info["publishers"] = publishers
    except:
        pass

    #Add short_description
    try:
        short_description = data["short_description"]
        game_info["short_description"] = short_description
    except:
        pass

    #Add metacritic score
    try:
        metacritic = data["metacritic"]["score"]
        game_info["metacritic_score"] = metacritic
    except:
        pass

    return game_info


def addInfo(df, index, dictInfo):
    for k,v in dictInfo.items():
        df.at[index, k] = v

    #df[index]

def extract(csvname):
    i = 1
    for index, row in df.iterrows():
        if math.isnan(df.at[index, "success"]):
            print(str(index) + " out of " + str(len(df)))
            i = i+1
            if i % 200 == 0:
                print("Waiting 1,5 minutes! (API Throttle Limit)")
                time.sleep(90)
            try:
                review_info = getReviewInfo(row["appid"])
                game_info = getGameInfo(row["appid"])
                addInfo(df, index, game_info)
                if review_info is not None:
                    addInfo(df, index, review_info)

                if i % 20 == 0:
                    df.to_csv(csvname+".csv", index = False)

            except:
                print(sys.exc_info()[0])
                continue
    df.to_csv(csvname + ".csv", index = False)


#extract(df, "fullSteamV4")
#extract(testDF, "newTest")

