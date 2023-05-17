import json
import requests
import datetime as dt


class DataManager:
    # This class is responsible for talking to the Google Sheet.
    def __init__(self):
        pass

    def history_discounts(self, id_game):
        history_list = []
        # Leer el contenido actual del archivo JSON
        try:
            with open("min_prices.json", "r", encoding="utf-8") as f_json:
                history_list = json.load(f_json)
        except FileNotFoundError:
            print("Not a file, creating a new one")
        finally:
            for i in range(len(history_list)):
                if id_game not in str(history_list[i]["appid"]):
                    history_list.append(self.find_game(id_game))

        # Escribir la lista actualizada de objetos JSON en el archivo
        with open("min_prices.json", "w", encoding="utf-8") as f_json:
            json.dump(history_list, f_json, indent=4)

    def find_game(self, id_game):
        steam_price_endpoint = f"http://store.steampowered.com/api/appdetails?appids={id_game}&cc=mx"
        steam_response = requests.get(url=steam_price_endpoint)
        steam_json = steam_response.json()
        game_price = {
            "name": steam_json[id_game]["data"]["name"],
            "date": str(dt.datetime.today()),
            "appid": id_game,
            "price_details": {
                "initial_price": steam_json[id_game]["data"]["price_overview"]["initial_formatted"],
                "final_price": steam_json[id_game]["data"]["price_overview"]["final_formatted"],
                "currency": steam_json[id_game]["data"]["price_overview"]["currency"],
                "discount": str(steam_json[id_game]["data"]["price_overview"]["discount_percent"]) + " %"
            }
        }
        return game_price


data_manager = DataManager()
data_manager.find_game(id_game="1286680")
data_manager.history_discounts(id_game="1286680")
