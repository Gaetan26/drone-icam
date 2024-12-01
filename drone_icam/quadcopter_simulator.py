

import dronekit_sitl, time
from dronekit import connect
from geopy.geocoders import Nominatim
import os.path


LAST_COORDINATES_FILE   = "data/quadcopter_simulator_last_used_coordinates.txt"
IPSTACK_API_KEY         = "3b09bf6c1f4a2fe92b218bfc70c53cea"
IPSTACK_API_ENDPOINT_A  = "http://api.ipstack.com/"
IPSTACK_API_ENDPOINT_B  = "http://api.ipstack.com/check"


def get_ip() -> str | None:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as test_socket:
        try:
            test_socket.connect(("8.8.8.8", 80))
            ip = test_socket.getsockname()[0]
        except Exception:
            ip = None
    return ip


def get_ip_location(ip:str = None) -> object | None:
    import requests
    
    endpoint = IPSTACK_API_ENDPOINT_B
    if ip is not None:
        endpoint = IPSTACK_API_ENDPOINT_A + ip

    req = requests.get( url = endpoint, params = { 'access_key':IPSTACK_API_KEY } )
    if req.status_code == 200:
        return req.json()
    else:
        return None


def init_vehicle(lat = -1.0, lng = -1.0) -> object:

    params_valid = False

    if lat != -1 or lng != -1:
        
        if not isinstance(lat, float):
            raise ValueError("lat is not a float")
        
        if not isinstance(lng, float):
            raise ValueError("lng is not a float")

        if lat == -1:
            raise ValueError("lat should be set")

        if lng == -1:
            raise ValueError("lng should be set")

        params_valid = True


    # gives 1 tries for the reverse geocoding
    if not params_valid:

        text_address, reverse_geo, ip = "", [], get_ip()

        if ip is None:
            print("you need an internet connection to continue, it seems that this is not the case!")
            exit()

        location = get_ip_location()
        location = ( (location['latitude'], location['longitude']), f"{location['region_name']},  {location['country_name']} ({location['continent_name']})" )
        reverse_geo.append(location)

        option_choosed = -1

        # read the file containing the last coordinates, if exists
        if os.path.isfile(LAST_COORDINATES_FILE):
            with open(LAST_COORDINATES_FILE, 'r', encoding="utf-8") as file:
                line = [ line.rstrip('\n') for line in file ]

                #tests if the files is of the correct size
                if len(line) == 3:
                    lat , lng , text_address = line
                    lat = float(lat)
                    lng = float(lng)

        # menu
        print("Select the address that bests describes your current location")
        print( "Press 1 to choose :" , reverse_geo[0][1]  )
        print( "Press 2 to enter an address manually")
        print( "Press 3 to enter the GPS coordinates manually")
        print( "Press 4 to reuse the last used coordinates (" + text_address + " : " + str(lat) + "," + str(lng) + ")")

        while option_choosed not in range(1,5):
            try:
                option_choosed = int(input("\nPlease enter your choice :\n"))

                if option_choosed == 1:
                    lat , lng =  reverse_geo[option_choosed - 1][0]
                    text_address = reverse_geo[option_choosed - 1][1]

                elif option_choosed == 2:
                    while True :
                        print("\tPlease enter a valid address (e.g. Unikin, UPN, Kimwenza-Mission )")
                        text_address = input("\t")
                        geo_locator = Nominatim(user_agent="icam-kinshasa")
                        try:
                            location = geo_locator.geocode(text_address)
                            time.sleep(.5)

                            if location:
                                print(f"\t=> {location}")
                                if input("\tis this the right address? (y/n) ") == "y":
                                    lat = location.latitude
                                    lng = location.longitude
                                    text_address = location.address
                                    print()
                                    break

                                print()
                            else:
                                print("\tthe address is not valid")
                                print()

                        except Exception as err:
                            print("\tthe address is not valid")
                            print()

                elif option_choosed == 3:
                    print("\tPlease enter the latitude (e.g. 47.340082)")
                    lat = input("\t")
                    print("\tPlease enter the longitude (e.g. -2.878657)")
                    lng = input("\t")
                    text_address= " "

                elif option_choosed == 4:
                    pass

            except :
                print("[ERROR] - Please enter a valid choice")
                option_choosed = -1

        with open(LAST_COORDINATES_FILE, 'w', encoding="utf-8") as the_file:
            the_file.write(str(lat) +'\n')
            the_file.write(str(lng) +'\n')
            the_file.write(text_address)


    sitl = dronekit_sitl.start_default(lat=lat , lon=lng)
    connection_string = sitl.connection_string()

    # Connect to the Vehicle
    print(f'Connecting to vehicle on: {connection_string}')
    vehicle = connect(connection_string, wait_ready=True)


    return vehicle

 
# Unitary Test 1
# 
# def test_init():
#     print("\n# PLEASE BE CAREFULL YOU ARE RUNNING THE TEST CASE ! #\n")
#     vehicle = init_vehicle()
#     input("Press ENTER key to interrupt...")
#     vehicle.close()
# 
# test_init()