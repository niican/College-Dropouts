import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk

location_urls = {
    "Dali": "Dali",
    "Zhongming": "jhongming",
    "Xitun": "situn",
    "Shalu": "shalu",
    "Changhua": "changhua",
    "Fengyuan": "fongyuan",
}

def get_air_quality(location):
    url = f"https://aqicn.org/city/taiwan/{location_urls[location]}/"
    print("Fetching URL:", url)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        air_quality_div = soup.find("div", class_="aqivalue")
        if air_quality_div:
            air_quality = air_quality_div.text.strip()
            return air_quality
        else:
            return "Air quality data not found"
    else:
        return "Error fetching data from aqicn.org"

def update_air_quality():
    selected_location = location_var.get()
    air_quality = get_air_quality(selected_location)
    result_label.config(text=f"Air quality for {selected_location}: {air_quality}")

root = tk.Tk()
root.title("Taiwan Air Quality Checker")

location_var = tk.StringVar(root)
location_dropdown = ttk.Combobox(root, textvariable=location_var, values=list(location_urls.keys()))
location_dropdown.grid(row=0, column=0, padx=10, pady=10)
location_dropdown.current(0)

update_button = ttk.Button(root, text="Check Air Quality", command=update_air_quality)
update_button.grid(row=0, column=1, padx=10, pady=10)

result_label = ttk.Label(root, text="")
result_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
