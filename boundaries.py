import os
import json
from shapely.geometry import shape, Point
import csv
import time

def check_id_exists(path_to_file):
    """
    path_to_file: path to geojson file. 

    Opens geojson and checks for an id.
    returns None if no id is found.
    """
    with open(path_to_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("id")

def check_point_contained(centroid, loc_code, path_to_file, level):
    """
    centroid: centroid in format Point(latitude,longitude)    
    loc_code: location_code.
    path_to_file: path to geojson file.
    level: level of the location.

    Opens geojson file and checks if centroid is contained. If yes, check if level matches with admin level.
    If yes, check if the geojson file has existing ID by calling check_id_exists.
    If file does not have existing id, call update_geojson to write in the id. 
    """
    global matches
    global result
    with open(path_to_file, "r", encoding="utf-8") as f:                    
        js = json.load(f) 
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(centroid):
            with open(path_to_file, encoding="utf-8") as f:
                matches += 1
                ans = path_to_file[16:]                                  
                result += ans+":"
                for item in js["features"]:
                    admin_level = abs(item['properties']['admin_level'])
                    if str(admin_level) == "2" and level == 0:
                        id_exist = check_id_exists(path_to_file)
                        if id_exist == None:
                            update_geojson(loc_code, path_to_file)
                    elif str(admin_level) == "4" and level == 1:
                        id_exist = check_id_exists(path_to_file)
                        if id_exist == None:
                            update_geojson(loc_code, path_to_file)


def update_geojson(loc_code, path_to_file):
    """
    loc_code: location_code to be written into geojson.

    Opens geojson and writes id.
    """
    with open(path_to_file,"r",encoding="utf-8") as f:
        id_to_write={"id":loc_code}
        updated_json = json.load(f)
        updated_json.update(id_to_write)
    with open(path_to_file,"w", encoding="utf-8") as write_to_geojson:
        write_to_geojson.write(json.dumps(updated_json,ensure_ascii=False))


with open("location_codes_final.csv", "r", newline="") as csv_file:
    read_csv = csv.DictReader(csv_file)
    
    with open("results_new-" + str(int(time.time())) + ".csv","w",newline='') as results_csv_file:
        fieldnames = ["location_code","location_name","local_fips_id","centroid","country","country_numeric_code","type","country_alpha_2_code","state_alpha_2_code","parent_location_id","level","assigned"]
        csv_writer = csv.DictWriter(results_csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        for line in read_csv:
            result = ""
            matches = 0
            loc_code = line["location_code"]
            centre_coord = line["centroid"]
            country_code = line["country_alpha_2_code"]
            location_type = line["type"]
            level = int(line["level"])
            # To fix some inconsistencies with the centroid formatting and get the coordinates only.
            if centre_coord.startswith("POINT "):
                centre_coord = centre_coord.replace("POINT ","Point")
            else:
                centre_coord = centre_coord.replace("POINT","Point")
            centre_coord = centre_coord.replace("Point(","")
            centre_coord = centre_coord.replace(")","")
            if "," in centre_coord:
                centre_coord = centre_coord.replace(","," ")
            lat , lng = centre_coord.split(" ")

            centroid = Point(float(lat),float(lng))

            if level == 0:
                filename = country_code+".geojson"
                path_to_file = ("boundaries/"+country_code+"/"+filename)
                if os.path.exists(path_to_file) == True:
                    check_point_contained(centroid, loc_code, path_to_file,level)
                             
            elif level == 1:
                directory = os.fsencode("boundaries/"+country_code+"/sub")
                if os.path.exists(directory) == True:
                    for file in os.listdir(directory):
                        filename = os.fsdecode(file)
                        if filename.endswith(".geojson"):                            
                            path_to_file = ("boundaries/"+country_code+"/sub/"+filename)
                            check_point_contained(centroid,loc_code, path_to_file,level)
            else:
                #skipped as level > 1 
                matches += 1
                result = ""

            if matches == 0:      
                result = "no"
                print(country_code + ", " + loc_code)
                             
            csv_writer.writerow({
                    "location_code": line["location_code"],
                    "location_name": line["location_name"],
                    "local_fips_id": line["local_fips_id"],
                    "centroid": line["centroid"],
                    "country": line["country"],
                    "country_numeric_code": line["country_numeric_code"],
                    "type":line["type"],
                    "country_alpha_2_code": line["country_alpha_2_code"],
                    "state_alpha_2_code": line["state_alpha_2_code"],
                    "parent_location_id":line["parent_location_id"],
                    "level":line["level"],
                    "assigned":result
                })
