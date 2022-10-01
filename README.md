# centroidChecker

This script reads the csv file "location_codes_final.csv".
Each line in the csv file contains a location code with its centroid coordinates and other information.
It checks if the centroid is contained inside the boundaries of the relevant geoJson files. 
If the boundary does contain the centroid, then it writes the file path of the geoJson to the line in a new column in the output csv file.
Also writes the location_code into the base of the matching geoJson as "id"
