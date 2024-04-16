import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

def get_lat_long(location_name):
    geolocator = Nominatim(user_agent="geo_locator")
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def extract_numeric_temperature(temperature_string):
    # Remove any leading or trailing whitespace
    temperature_string = temperature_string.strip()

    # Extract numeric part from the string
    numeric_part = ''.join(char for char in temperature_string if char.isdigit() or char == '.')

    # Convert the numeric part to integer or float
    numeric_temperature = int(float(numeric_part)) if '.' in numeric_part else int(numeric_part)
    return numeric_temperature

def convert_fahrenheit_to_celsius(fahrenheit):
    celsius = int((fahrenheit - 32) * 5 / 9)
    return celsius

def get_weather(latitude, longitude):
    url = f"https://weather.com/weather/today/l/{latitude},{longitude}?par=google"
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Temperature
        temperature_span = soup.find("span", class_="CurrentConditions--tempValue--MHmYY")
        temperature = temperature_span.text if temperature_span else "Temperature not found"
        temperature = convert_fahrenheit_to_celsius(extract_numeric_temperature(temperature))

        # Extract Current Condition
        current_condition_div = soup.find('div', class_='CurrentConditions--phraseValue--mZC_p')
        current_condition = current_condition_div.text.strip()

        # Extract Day and Night Temperatures
        day_night_temp_div = soup.find('div', class_='CurrentConditions--tempHiLoValue--3T1DG')
        if day_night_temp_div:
            day_temp, night_temp = day_night_temp_div.find_all('span', {'data-testid': 'TemperatureValue'})
            day_temperature = day_temp.text.strip()
            day_temperature = convert_fahrenheit_to_celsius(extract_numeric_temperature(day_temperature))
            night_temperature = night_temp.text.strip()
            night_temperature = convert_fahrenheit_to_celsius(extract_numeric_temperature(night_temperature))
        
        return temperature, current_condition, day_temperature, night_temperature
    else:
        return "Weather information not available."

def main():
    location_name = "Yogyakarta, Indonesia"
    latitude, longitude = get_lat_long(location_name)
    if latitude is not None and longitude is not None:
##        print(f"Latitude: {latitude}, Longitude: {longitude}")
        weather = get_weather(latitude, longitude)
        print(f"Weather condition: {weather[0]}°C")
        print(f"Current condition: {weather[1]}")
        print(f"Day Temperature: {weather[2]}°C")
        print(f"Night Temperature: {weather[3]}°C")
    else:
        print("Location not found.")

if __name__ == "__main__":
    main()
