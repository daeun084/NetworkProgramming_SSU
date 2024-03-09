from geopy.geocoders import Nominatim

if __name__ == '__main__':
    address = 'Soongsil University'
    user_agent = 'Daeun'
    location = Nominatim(user_agent=user_agent).geocode(address)
    print(location.latitude, location.longitude)

