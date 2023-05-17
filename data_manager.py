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

    def get_history_list(self):
        response = requests.get(url=self.sheety_endpoint, headers=self.sheety_headers)
        return response.json()["historico"]

    def create_game_entry(self, id_game):
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
        if response.status_code == 200:
            print("Adding new game")

    def delete_game_entry(self, row_id):
        delete_row = f"{self.sheety_endpoint}/{row_id}"
        response = requests.delete(url=delete_row, headers=self.sheety_headers)
        if response.status_code == 200:
            print(f"Deleting game entry at row {row_id}")

    def update_game_entry(self, row_id, final_price, discount):
        sheety_PUT_params = {
            "historico": {
                "modifyDate": self.TODAY,
                "finalPrice": final_price,
                "discount": discount
            }
        }
        update_game = f"{self.sheety_endpoint}/{row_id}"
        response = requests.put(url=update_game, headers=self.sheety_headers, json=sheety_PUT_params)
        if response.status_code == 200:
            print("updated game successfully")

    def game_exists(self, id_game):
        history_list = self.get_history_list()
        for item in history_list:
            if id_game == str(item.get("appId")):
                print("Game exists")
                return True, item

    def update_entries(self):
        history_list = self.get_history_list()
        for item in history_list:
            modify_date = dt.datetime.strptime(item["modifyDate"], "%d-%b-%Y")
            if modify_date < dt.datetime.today() and item["finalPrice"] > \
                    self.find_game(item["appId"])["price_details"]["final_price"]:
                self.update_game_entry(item["id"], self.find_game(item["appId"])["price_details"]["final_price"],
                                       self.find_game(item["appId"])["price_details"]["discount"])
                print("entries updated")

    def history_discounts(self, id_game):
        exists = self.game_exists(id_game)
        if exists[0]:
            self.update_entries()
        else:
            self.create_game_entry(id_game)

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
# data_manager.update_entries()
