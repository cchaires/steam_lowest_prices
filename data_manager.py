import json
import requests
import datetime as dt
from dotenv import load_dotenv
import os
load_dotenv()


class DataManager:
    # This class is responsible for talking to the Google Sheet.
    def __init__(self):
        self.sheety_headers = {
            "Authorization": os.getenv("AUTHORIZATION")
        }
        self.sheety_endpoint = \
            "https://api.sheety.co/d902c2d4b30f97095a96290aec50a74b/steamLowestPriceHistory/historico"
        self.TODAY = dt.datetime.today().strftime("%d-%b-%Y")

    def game_post(self, id_game):
        game_info = self.find_game(id_game)
        sheety_POST_params = {
            "historico": {
                "name": game_info["name"],
                "appId": game_info["appid"],
                "creationDate": self.TODAY,
                "modifyDate": self.TODAY,
                "initialPrice": game_info["price_details"]["initial_price"],
                "finalPrice": game_info["price_details"]["final_price"],
                "currency": game_info["price_details"]["currency"],
                "discount": game_info["price_details"]["discount"]
            }
        }
        response = requests.post(url=self.sheety_endpoint, headers=self.sheety_headers, json=sheety_POST_params)
        print(response.status_code)

    def game_exists(self, id_game):
        response = requests.get(url=self.sheety_endpoint, headers=self.sheety_headers)
        history_list = response.json()["historico"]
        for item in history_list:
            if id_game == str(item.get("appId")):
                return True, item

    def delete_game(self, id_game):
        search = self.game_exists(id_game)
        rowID = search[1].get("id")
        delete_row = \
            f"https://api.sheety.co/d902c2d4b30f97095a96290aec50a74b/steamLowestPriceHistory/historico/{rowID}"
        delete = requests.delete(url=delete_row, headers=self.sheety_headers)

    def update_game(self, id_game, row_id):
        game_info = self.find_game(id_game)
        list = self.game_exists(id_game)
        modify_date = dt.datetime.strptime(list[1]["modifyDate"], "%d-%b-%Y")
        if modify_date < dt.datetime.today() and list[1]["finalPrice"] > \
                self.find_game(list[1]["appId"])["price_details"]["final_price"]:
            sheety_PUT_params = {
                "historico": {
                    "modifyDate": self.TODAY,
                    "finalPrice": game_info["price_details"]["final_price"],
                    "discount": game_info["price_details"]["discount"]
                }
            }
            update_game = \
                f"https://api.sheety.co/d902c2d4b30f97095a96290aec50a74b/steamLowestPriceHistory/historico/{row_id}"
            requests.put(url=update_game, headers=self.sheety_headers, json=sheety_PUT_params)

    def history_discounts(self, id_game):
        exists = self.game_exists(id_game)
        if exists[0]:
            self.update_game(id_game, exists[1].get("id"))
        else:
            self.game_post(id_game)

    def find_game(self, id_game):
        steam_price_endpoint = f"http://store.steampowered.com/api/appdetails?appids={id_game}&cc=mx"
        steam_response = requests.get(url=steam_price_endpoint)
        steam_json = steam_response.json()
        game_price = {
            "name": steam_json[id_game]["data"]["name"],
            "date": self.TODAY,
            "appid": id_game,
            "price_details": {
                "initial_price": steam_json[id_game]["data"]["price_overview"]["initial"] / 100,
                "final_price": steam_json[id_game]["data"]["price_overview"]["final"] / 100,
                "currency": steam_json[id_game]["data"]["price_overview"]["currency"],
                "discount": str(steam_json[id_game]["data"]["price_overview"]["discount_percent"]) + " %"
            }
        }
        return game_price


data_manager = DataManager()
# data_manager.find_game(id_game="233290")
data_manager.history_discounts(id_game="233290")
# data_manager.delete_game(id_game="1243830")
