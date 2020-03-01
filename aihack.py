# _  __  __       _       _        ____
#  |  \/  | __ _| |_ ___| |__    / ___| __ _ _ __ ___   ___
#  | |\/| |/ _` | __/ __| '_ \  | |  _ / _` | '_ ` _ \ / _ \
#  | |  | | (_| | || (__| | | | | |_| | (_| | | | | | |  __/
#  |_|  |_|\__,_|\__\___|_| |_|  \____|\__,_|_| |_| |_|\___|
#
botName = "samson2ky-defbot"
import requests
import json
from random import sample, choice
from time import sleep

# See our help page to learn how to get a WEST EUROPE Microsoft API Key at
#  https://help.aigaming.com/game-help/signing-up-for-azure
#                                              *** Use westeurope API key for best performance ***
headers_vision = {"Ocp-Apim-Subscription-Key": API KEY}
vision_base_url = "https://westeurope.api.cognitive.microsoft.com/vision/v2.0/"
params_analyse = {
    "visualFeatures": "categories,tags,description,faces,imageType,color,adult",
    "details": "celebrities,landmarks",
}
analysed_tilestiles = []
previous_move = [0, 0]
move_number = 0
global_tiles = []


def calculate_move(gamestate):
    global analysed_tiles
    global global_tiles
    global previous_move
    global move_number
    global params_analyse

    if previous_move[1] < 35:
        if previous_move[1] == 0:
            for index in range(len(gamestate["TileBacks"])):
                global_tiles.append({})
                analyse_url = vision_base_url + "ocr"
                data = {"url": gamestate["TileBacks"][index]}
                msapi_response = microsoft_api_call(
                    analyse_url, params_analyse, headers_vision, data
                )
                category = msapi_response["regions"][0]["lines"][0]["words"][0][
                    "text"
                ].lower()
                global_tiles[index]["index"] = index
                global_tiles[index]["matched"] = None
                global_tiles[index]["subject"] = None
                global_tiles[index]["category"] = category
            previous_move[0] = 0
            previous_move[1] = 1
        elif gamestate["UpturnedTiles"] == [] and previous_move != []:
            global_tiles[previous_move[0]]["matched"] = "matched"
            global_tiles[previous_move[1]]["matched"] = "matched"
            previous_move[0] = previous_move[0] + 1
            previous_move[1] = previous_move[0] + 1
        else:
            for x in range(len(gamestate["UpturnedTiles"])):
                print("helelelelelel")
                index = previous_move[x]
                url = gamestate["UpturnedTiles"][x]["Tile"]
                if global_tiles[index]["category"] == "landmark":
                    analyse_url = vision_base_url + "analyze"
                    data = {"url": url}

                    msapi_response = microsoft_api_call(
                        analyse_url, params_analyse, headers_vision, data
                    )

                    subject = check_for_landmark(msapi_response)
                    global_tiles[index]["subject"] = subject

                elif global_tiles[index]["category"] == "animal":
                    analyse_url = vision_base_url + "analyze"
                    data = {"url": url}
                    msapi_response = microsoft_api_call(
                        analyse_url, params_analyse, headers_vision, data
                    )
                    subject = check_for_animal(msapi_response, gamestate["AnimalList"])
                    global_tiles[index]["subject"] = subject

                else:
                    analyse_url = vision_base_url + "ocr"
                    data = {"url": url}
                    msapi_response = microsoft_api_call(
                        analyse_url, params_analyse, headers_vision, data
                    )
                    subject = check_for_text(url)
                    global_tiles[index]["subject"] = subject

            previous_move[0] = previous_move[0] + 1
            previous_move[1] = previous_move[0] + 1

    if previous_move[1] == 35:

        for x in range(36):
            if (
                global_tiles[x]["subject"] != None
                and global_tiles[x]["matched"] == None
                and global_tiles[x]["category"]
                == gamestate["Bonus"][: len(gamestate["Bonus"]) - 1].lower()
            ):
                global_tiles[x]["matched"] = "matched"
                tile1 = global_tiles[x]

                for index in range(global_tiles[x]["index"] + 1, 36):
                    tile1 = global_tiles[x]

                    if global_tiles[index]["subject"] == tile1["subject"]:
                        global_tiles[index]["matched"] = "matched"

                        print(global_tiles[index])
                        print(tile1)

                        previous_move[1] = 38
                        print({"Tiles": [tile1["index"], global_tiles[index]["index"]]})
                        return {"Tiles": [tile1["index"], global_tiles[index]["index"]]}

    if previous_move[1] == 38:
        for x in range(36):

            if (
                global_tiles[x]["subject"] != None
                and global_tiles[x]["matched"] == None
                and global_tiles[x]["category"]
                == gamestate["Bonus"][: len(gamestate["Bonus"]) - 1].lower()
            ):
                tile1 = global_tiles[x]
                global_tiles[x]["matched"] = "matched"
                print(tile1)
                print(gamestate["Bonus"])

                for index in range(global_tiles[x]["index"] + 1, 36):
                    tile1 = global_tiles[x]

                    if global_tiles[index]["subject"] == tile1["subject"]:
                        global_tiles[index]["matched"] = "matched"

                        print(global_tiles[index])
                        print(tile1)

                        previous_move[1] = 38
                        print({"Tiles": [tile1["index"], global_tiles[index]["index"]]})
                        return {"Tiles": [tile1["index"], global_tiles[index]["index"]]}

    print(global_tiles)
    print(previous_move)
    print(len(global_tiles))
    return {"Tiles": previous_move}


def check_for_animal(msapi_response, animal_list):

    subject = None

    if "tags" in msapi_response:

        for tag in sorted(
            msapi_response["tags"], key=lambda x: x["confidence"], reverse=True
        ):

            if "name" in tag and tag["name"] in animal_list:

                subject = tag["name"].lower()

                break

    return subject


#
def check_for_landmark(msapi_response):

    print(msapi_response)

    subject = None

    if "categories" in msapi_response and msapi_response["categories"] != []:
        print("checkking inside landmoark")
        if "detail" in msapi_response["categories"][0]:
            if (
                "landmarks" in msapi_response["categories"][0]["detail"]
                and msapi_response["categories"][0]["detail"]["landmarks"] != []
            ):
                subject = msapi_response["categories"][0]["detail"]["landmarks"][0][
                    "name"
                ].lower()

    return subject


def check_for_text(url):
    subject = None

    analyse_url = vision_base_url + "ocr"
    params_analyse = {
        "visualFeatures": "categories,tags,description,faces,imageType,color,adult",
        "details": "celebrities,landmarks",
    }
    data = {"url": url}
    msapi_response = microsoft_api_call(
        analyse_url, params_analyse, headers_vision, data
    )
    print(msapi_response)
    print("ocr is: {}".format(msapi_response))
    if msapi_response["regions"] != []:
        subject = msapi_response["regions"][0]["lines"][0]["words"][0]["text"]

    return subject


def microsoft_api_call(url, params, headers, data):
    # Make API request
    response = requests.post(url, params=params, headers=headers, json=data)
    # Convert result to JSON
    res = response.json()
    # While we have exceeded our request volume quota
    while "error" in res and res["error"]["code"] == "429":
        # Wait for 1 second
        sleep(1)
        # Print that we are retrying the API call here ----------------->
        print("Retrying")
        # Make API request
        response = requests.post(url, params=params, headers=headers, json=data)
        # Convert result to JSON
        res = response.json()

    return res


def valid_subscription_key():
    # Make a computer vision api call
    test_api_call = microsoft_api_call(
        vision_base_url + "analyze", {}, headers_vision, {}
    )

    if "error" in test_api_call:
        raise ValueError(
            "Invalid Microsoft Computer Vision API key for current region: {}".format(
                test_api_call
            )
        )


# Check the subscription key
valid_subscription_key()
