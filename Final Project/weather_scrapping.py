import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from customtkinter import *
from tkintermapview import TkinterMapView
import re

#-----------------------------

def get_lat_long(location_name):
    geolocator = Nominatim(user_agent="geo_locator")
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def extract_numeric_temperature(temperature_string):
    temperature_string = temperature_string.strip()
    numeric_part = ''.join(char for char in temperature_string if char.isdigit() or char == '.')
    if numeric_part:
        numeric_temperature = int(float(numeric_part))
        return numeric_temperature
    else:
        return None

def convert_fahrenheit_to_celsius(fahrenheit):
    if fahrenheit is not None:
        celsius = int((fahrenheit - 32) * 5 / 9)
        return celsius
    else:
        return None

def get_today_place_forecast(soup):
    today_forecast = soup.find('div', id='WxuTodayWeatherCard-main-486ce56c-74e0-4152-bd76-7aea8e98520a')
    if not today_forecast:
        return "", pd.DataFrame()

    header_element = today_forecast.find('header', class_='Card--cardHeader--3NRFf').text.strip()

    temperature_elements = today_forecast.find_all('div', class_='Column--temp--1sO_J Column--verticalStack--28b4K')
    precipitation_elements = today_forecast.find_all('div', class_='Column--precip--3JCDO')
    time_elements = today_forecast.find_all('h3', class_='Column--label--2s30x Column--default--2-Kpw Column--verticalStack--28b4K')

    temperatures = [temp.find('span', attrs={'data-testid': 'TemperatureValue'}).text.strip() for temp in temperature_elements]
    precipitations = [precip.find('span', class_='Column--precip--3JCDO').text.strip() for precip in precipitation_elements]
    times = [time.find('span', class_='Ellipsis--ellipsis--3ADai').text.strip() for time in time_elements]

    new_temperatures = [f"{convert_fahrenheit_to_celsius(extract_numeric_temperature(temp))}°C" for temp in temperatures]

    min_length = min(len(times), len(new_temperatures), len(precipitations))
    times = times[:min_length]
    new_temperatures = new_temperatures[:min_length]
    precipitations = precipitations[:min_length]

    df_today_forecast = pd.DataFrame({'Time': times, 'Temperature (°C)': new_temperatures, 'Precipitation': precipitations})
    return header_element, df_today_forecast

def todays_weather(soup):
    weather_today = soup.find('div', id='todayDetails')
    if not weather_today:
        return "", pd.DataFrame()

    header_element = weather_today.find('header', class_='Card--cardHeader--3NRFf').text.strip()

    weather_elements = weather_today.find_all('div', class_='WeatherDetailsListItem--label--2ZacS')
    weather_data = weather_today.find_all('div', class_='WeatherDetailsListItem--wxData--kK35q')

    labels = []
    datas = []

    if weather_data:
        data = weather_data[0].text.strip()
        split_data = data.split('/')
        high_temp = split_data[0]
        low_temp = split_data[1]
        high_temp = convert_fahrenheit_to_celsius(extract_numeric_temperature(high_temp))
        low_temp = convert_fahrenheit_to_celsius(extract_numeric_temperature(low_temp))
    else:
        high_temp = None
        low_temp = None

    for label, data in zip(weather_elements, weather_data):
        labels.append(label.text.strip())
        datas.append(data.text.strip())

    if labels and datas:
        datas[0] = f"{high_temp}°C/{low_temp}°C" if high_temp is not None and low_temp is not None else "N/A"

    df_weather_today = pd.DataFrame({'Label': labels, 'Data': datas})
    return header_element, df_weather_today

def hourly_forecast(soup):
    hourly_forecast = soup.find('div', id='WxuHourlyWeatherCard-main-29584a07-3742-4598-bc2a-f950a9a4d900')
    if not hourly_forecast:
        return "", pd.DataFrame()

    header_element = hourly_forecast.find('header', class_='Card--cardHeader--3NRFf').text.strip()

    temperature_elements = hourly_forecast.find_all('div', class_='Column--temp--1sO_J Column--verticalStack--28b4K')
    precipitation_elements = hourly_forecast.find_all('div', class_='Column--precip--3JCDO')
    time_elements = hourly_forecast.find_all('h3', class_='Column--label--2s30x Column--default--2-Kpw Column--verticalStack--28b4K')

    temperatures = [temp.find('span', attrs={'data-testid': 'TemperatureValue'}).text.strip() for temp in temperature_elements]
    precipitations = [precip.find('span', class_='Column--precip--3JCDO').text.strip() for precip in precipitation_elements]
    times = [time.find('span', class_='Ellipsis--ellipsis--3ADai').text.strip() for time in time_elements]

    new_temperatures = [f"{convert_fahrenheit_to_celsius(extract_numeric_temperature(temp))}°C" for temp in temperatures]

    min_length = min(len(times), len(new_temperatures), len(precipitations))
    times = times[:min_length]
    new_temperatures = new_temperatures[:min_length]
    precipitations = precipitations[:min_length]

    df_hourly_forecast = pd.DataFrame({'Time': times, 'Temperature (°C)': new_temperatures, 'Precipitation': precipitations})
    return header_element, df_hourly_forecast

def daily_forecast(soup):
    daily_forecast = soup.find('div', id='WxuDailyWeatherCard-main-bb1a17e7-dc20-421a-b1b8-c117308c6626')
    if not daily_forecast:
        return "", pd.DataFrame()

    header_element = daily_forecast.find('header', class_='Card--cardHeader--3NRFf').text.strip()

    temperature_elements = daily_forecast.find_all('div', class_='Column--temp--1sO_J Column--verticalStack--28b4K')
    precipitation_elements = daily_forecast.find_all('div', class_='Column--precip--3JCDO')
    time_elements = daily_forecast.find_all('h3', class_='Column--label--2s30x Column--default--2-Kpw Column--verticalStack--28b4K')

    temperatures = [temp.find('span', attrs={'data-testid': 'TemperatureValue'}).text.strip() for temp in temperature_elements]
    precipitations = [precip.find('span', class_='Column--precip--3JCDO').text.strip() for precip in precipitation_elements]
    times = [time.find('span', class_='Ellipsis--ellipsis--3ADai').text.strip() for time in time_elements]

    new_temperatures = [f"{convert_fahrenheit_to_celsius(extract_numeric_temperature(temp))}°C" for temp in temperatures]

    min_length = min(len(times), len(new_temperatures), len(precipitations))
    times = times[:min_length]
    new_temperatures = new_temperatures[:min_length]
    precipitations = precipitations[:min_length]

    df_daily_forecast = pd.DataFrame({'Time': times, 'Temperature (°C)': new_temperatures, 'Precipitation': precipitations})
    return header_element, df_daily_forecast

def get_weather(latitude, longitude):
    global df_today_forecast, df_weather_today, temperature_today, condition_span, temperatureDN, df_hourly_forecast, df_daily_forecast, data_to_save, actual_location
    url = f"https://weather.com/weather/today/l/{latitude},{longitude}?par=google"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        temperature_span = soup.find("span", class_="CurrentConditions--tempValue--MHmYY")
        temperature = temperature_span.text if temperature_span else "Temperature not found"
        temperature_today = convert_fahrenheit_to_celsius(extract_numeric_temperature(temperature))
        
        weather_details = f"Current Temperature: {temperature_today}°C\n\n"

        condition_span = soup.find("div", class_="CurrentConditions--phraseValue--mZC_p").text.strip()
        # print(condition_span)

        temperatureDN_span = soup.find("div", class_="CurrentConditions--tempHiLoValue--3T1DG").text.strip()
        # print(temperatureDN_span)

        pattern = r'(\d+)°'
        temperaturesDN = re.findall(pattern, temperatureDN_span)
        temperaturesDN = [convert_fahrenheit_to_celsius(int(temp)) for temp in temperaturesDN]
        # print(temperaturesDN)
        temperatureDN = f"Day {temperaturesDN[0]}° • Night {temperaturesDN[1]}°"
        # print(temperatureDN)

        header1, df_today_forecast = get_today_place_forecast(soup)
        weather_details += header1 + "\n" + df_today_forecast.to_string(index=False) + "\n\n"

        header2, df_weather_today = todays_weather(soup)
        weather_details += header2 + "\n" + df_weather_today.to_string(index=False) + "\n\n"

        header3, df_hourly_forecast = hourly_forecast(soup)
        weather_details += header3 + "\n" + df_hourly_forecast.to_string(index=False) + "\n\n"

        header4, df_daily_forecast = daily_forecast(soup)
        weather_details += header4 + "\n" + df_daily_forecast.to_string(index=False) + "\n\n"

        data_to_save = [
            (header1, df_today_forecast),
            (header2, df_weather_today),
            (header3, df_hourly_forecast),
            (header4, df_daily_forecast)
        ]
        match = re.search(r'(?<=Forecast for )[^"]+', header1)
        if match:
            actual_location = match.group(0)
            

        return weather_details
    else:
        return "Weather information not available."

def export_to_csv():
# Loop through each header and DataFrame pair
    for header_element, df in data_to_save:
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Replace any non-alphanumeric characters in header element
        filename = "".join(char if char.isalnum() else "_" for char in header_element)
        # Export DataFrame to CSV file
        df.to_csv(f"{filename}_{timestamp}.csv", index=False)
        print(f"{filename}_{timestamp}.csv succesfully exported")

#-------------------------------

def dropdown_func(event):
    global dropdown_data
    dropdown_data = combobox.get()
    # print(dropdown_data)
    # print(type(dropdown_data))

    if dropdown_data == "Hourly Forecast": 
        data_list1 = df_hourly_forecast.values.tolist()
        # print(dropdown_data)
    elif dropdown_data == "Daily Forecast":
        # print(dropdown_data)
        data_list1 = df_daily_forecast.values.tolist()
    # print(data_list1)
    # for i, row in enumerate(data_list1):
    #     for j, value in enumerate(row):
    #         label = CTkLabel(Daily_frame, text=f" {value} ")
    #         label.grid(row=i+1, column=j)

    # Daily_frame1
    label1.configure(text=data_list1[0][0])    
    label2.configure(text=data_list1[0][1], font=("TkDefaultFont", 30))
    label3.configure(text=data_list1[0][2])

    label4.configure(text=data_list1[1][0])
    label5.configure(text=data_list1[1][1], font=("TkDefaultFont", 30))
    label6.configure(text=data_list1[1][2])

    # Third set of labels
    label7.configure(text=data_list1[2][0])
    label8.configure(text=data_list1[2][1], font=("TkDefaultFont", 30))
    label9.configure(text=data_list1[2][2])

    # Fourth set of labels
    label10.configure(text=data_list1[3][0])
    label11.configure(text=data_list1[3][1], font=("TkDefaultFont", 30))
    label12.configure(text=data_list1[3][2])

    # Fifth set of labels
    label13.configure(text=data_list1[4][0])
    label14.configure(text=data_list1[4][1], font=("TkDefaultFont", 30))
    label15.configure(text=data_list1[4][2])

def show():
    global label1, label2, label3, label4, label5, label6, label7, label8, label9, label10, label11, label12, label13, label14, label15
    #--------------------------------------- today condition
    TodayCon_label = CTkLabel(TodayCon_frame, text=f" Today Condition ")
    TodayCon_label.grid(row=0, column=0, columnspan = 3)

    TodayCon_Label1 = CTkLabel(TodayCon_frame, text=actual_location)
    TodayCon_Label1.grid(row=1, column=0, columnspan = 3)

    TodayCon_Label2 = CTkLabel(TodayCon_frame, text=f"Lat : {latitude:.2f}\nLong : {longitude:.2f}")
    TodayCon_Label2.grid(row=2, column=0, columnspan = 3)

    TodayCon_Label3 = CTkLabel(TodayCon_frame, text=f"{temperature_today}°C", font=("TkDefaultFont", 50))
    TodayCon_Label3.grid(row=3, column=0, columnspan = 3)

    TodayCon_Label4 = CTkLabel(TodayCon_frame, text=condition_span)
    TodayCon_Label4.grid(row=4, column=0, columnspan = 3)

    TodayCon_Label5 = CTkLabel(TodayCon_frame, text=temperatureDN)
    TodayCon_Label5.grid(row=5, column=0, columnspan = 3)
    
    #------------------------------------------------------weather today
    data_list = df_weather_today.values.tolist()

    for i, row in enumerate(data_list):
        for j, value in enumerate(row):
            label = CTkLabel(WeToday_frame, text=f" {value} ")
            label.grid(row=i+1, column=j)

    #------------------------------------------------------weather today
    data_list1 = df_hourly_forecast.values.tolist()

    label1 = CTkLabel(Forecast_frame0, text=data_list1[0][0])
    label1.grid(row=0, column=0)
    label2 = CTkLabel(Forecast_frame0, text=data_list1[0][1], font=("TkDefaultFont", 30))
    label2.grid(row=1, column=0)
    label3 = CTkLabel(Forecast_frame0, text=data_list1[0][2])
    label3.grid(row=2, column=0)

    label4 = CTkLabel(Forecast_frame1, text=data_list1[1][0])
    label4.grid(row=0, column=0)
    label5 = CTkLabel(Forecast_frame1, text=data_list1[1][1], font=("TkDefaultFont", 30))
    label5.grid(row=1, column=0)
    label6 = CTkLabel(Forecast_frame1, text=data_list1[1][2])
    label6.grid(row=2, column=0)

    # Third set of labels
    label7 = CTkLabel(Forecast_frame2, text=data_list1[2][0])
    label7.grid(row=0, column=0)
    label8 = CTkLabel(Forecast_frame2, text=data_list1[2][1], font=("TkDefaultFont", 30))
    label8.grid(row=1, column=0)
    label9 = CTkLabel(Forecast_frame2, text=data_list1[2][2])
    label9.grid(row=2, column=0)

    # Fourth set of labels
    label10 = CTkLabel(Forecast_frame3, text=data_list1[3][0])
    label10.grid(row=0, column=0)
    label11 = CTkLabel(Forecast_frame3, text=data_list1[3][1], font=("TkDefaultFont", 30))
    label11.grid(row=1, column=0)
    label12 = CTkLabel(Forecast_frame3, text=data_list1[3][2])
    label12.grid(row=2, column=0)

    # Fifth set of labels
    label13 = CTkLabel(Forecast_frame4, text=data_list1[4][0])
    label13.grid(row=0, column=0)
    label14 = CTkLabel(Forecast_frame4, text=data_list1[4][1], font=("TkDefaultFont", 30))
    label14.grid(row=1, column=0)
    label15 = CTkLabel(Forecast_frame4, text=data_list1[4][2])
    label15.grid(row=2, column=0)

    #---------------------------------------- today forecast
    data_list2 = df_today_forecast.values.tolist()
    # print(data_list2)

    labels0 = CTkLabel(TodayCon_frame, text=f"\nToday Forecast")
    labels0.grid(row=6, column=0, columnspan=3)

    labels1 = CTkLabel(TodayCon_frame, text=data_list2[0][0])
    labels1.grid(row=7, column=0)
    labels2 = CTkLabel(TodayCon_frame, text=f"  {data_list2[0][1]}  ")
    labels2.grid(row=7, column=1)
    labels3 = CTkLabel(TodayCon_frame, text=data_list2[0][2])
    labels3.grid(row=7, column=2)

    labels4 = CTkLabel(TodayCon_frame, text=data_list2[1][0])
    labels4.grid(row=8, column=0)
    labels5 = CTkLabel(TodayCon_frame, text=f"  {data_list2[1][1]}  ")
    labels5.grid(row=8, column=1)
    labels6 = CTkLabel(TodayCon_frame, text=data_list2[1][2])
    labels6.grid(row=8, column=2)

    # Third set of labels
    labels7 = CTkLabel(TodayCon_frame, text=data_list2[2][0])
    labels7.grid(row=9, column=0)
    labels8 = CTkLabel(TodayCon_frame, text=f"  {data_list2[2][1]}  ")
    labels8.grid(row=9, column=1)
    labels9 = CTkLabel(TodayCon_frame, text=data_list2[2][2])
    labels9.grid(row=9, column=2)

    # Fourth set of labels
    labels10 = CTkLabel(TodayCon_frame, text=data_list2[3][0])
    labels10.grid(row=10, column=0)
    labels11 = CTkLabel(TodayCon_frame, text=f"  {data_list2[3][1]}  ")
    labels11.grid(row=10, column=1)
    labels12 = CTkLabel(TodayCon_frame, text=data_list2[3][2])
    labels12.grid(row=10, column=2)
    
def get_location():
    global location_name, latitude, longitude
        # Clear the displayed data in the Treeview widget
    for item in TodayCon_frame.winfo_children():
        item.destroy()

    location_name = location_entry.get()
    latitude, longitude = get_lat_long(location_name)
    maps(latitude, longitude)
    url = f"https://weather.com/weather/today/l/{latitude},{longitude}?par=google"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    if latitude is not None and longitude is not None:
        # header1, df1 = get_today_place_forecast(soup)
        # weather_info = 
        get_weather(latitude, longitude)
        show()
    else:
        messagebox.showerror("Error", "Location not found.")

def maps(latitude, longitude):
    # Clear previous map
    for widget in Maps_frame.winfo_children():
        widget.destroy()

    gmap = TkinterMapView(Maps_frame)
    gmap.pack(fill="both", expand=True)

    # Corrected tile server URL
    gmap.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga")
    # gmap.set_tile_server(f"https://www.google.com/maps/@{lat},{lng},8z")

    # Commented out the line to set the address
    gmap.set_position(latitude, longitude, marker=True)
    # gmap.set_address(location_name1, marker=True)
    # print(location_name1)

    gmap.set_zoom(8)

def main():
    global location_entry, Maps_frame,TodayCon_frame, combobox, WeToday_frame, Forecast_frame0, Forecast_frame1, Forecast_frame2, Forecast_frame3, Forecast_frame4 #Daily_frame, Daily_frame1, Daily_frame2, Daily_frame3, Daily_frame4
    root = CTk()
    # root.geometry("500x500")
    root.title("Actual Weather Srapping")

    #---------------------------------------------------------bagian atas

    location_label = CTkLabel(root, text=" Enter location: ")
    location_label.grid(row=0, column=0, padx=5, pady=5)

    location_entry = CTkEntry(root)
    location_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

    get_weather_button = CTkButton(root, text="Get Weather", command=get_location)
    get_weather_button.grid(row=0, column=4, padx=5, pady=5, sticky=(tk.W, tk.E))

    save_weather_button = CTkButton(root, text="Save Data", command=export_to_csv) #----------------------- modify nnti
    save_weather_button.grid(row=0, column=5, padx=5, pady=5, sticky=(tk.W, tk.E))

    #---------------------------------------------------------Today condition
    TodayCon_frame = CTkFrame(root)
    TodayCon_frame.grid(row=1, column=0, rowspan=3, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    #---------------------------------------------------------weather today

    WeToday_frame = CTkFrame(root)
    WeToday_frame.grid(column=1, row=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    #---------------------------------------------------------maps

    Maps_frame = CTkFrame(root, width=150)
    Maps_frame.grid(row=1, column=3, columnspan=5, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    #------------------------- forecast
    dropdonw_list = ["Hourly Forecast", "Daily Forecast"]

    combobox = ttk.Combobox(root, values=dropdonw_list)
    combobox.grid(row=2, column=1)
    # combobox.pack(pady=10)
    default_value = "Hourly Forecast"
    combobox.set(default_value)
    combobox.bind("<<ComboboxSelected>>", dropdown_func)

    Forecast_frame0 = CTkFrame(root)
    Forecast_frame0.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    Forecast_frame1 = CTkFrame(root)
    Forecast_frame1.grid(row=3, column=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    Forecast_frame2 = CTkFrame(root)
    Forecast_frame2.grid(row=3, column=3, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    Forecast_frame3 = CTkFrame(root)
    Forecast_frame3.grid(row=3, column=4, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    Forecast_frame4 = CTkFrame(root)
    Forecast_frame4.grid(row=3, column=5, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    root.mainloop()

if __name__ == "__main__":
    main()