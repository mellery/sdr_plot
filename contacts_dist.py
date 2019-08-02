import geopy.distance
import csv

home_coords = (37.203972, -80.241366)

max_dist = 0
min_dist = 100000000
max_contact = ""
min_contact = ""

with open("contacts_latlon.txt") as f:
    readf = csv.reader(f, delimiter=',')
    for row in readf:
        contact_coords = (row[1], row[2])
        distance = geopy.distance.distance(home_coords, contact_coords).miles
        #print(distance)
        if distance > max_dist:
            max_dist = distance
            max_contact = row[0]
            max_country = row[3]
        if distance < min_dist:
            min_dist = distance
            min_contact = row[0]
            min_country = row[3]

print("max",max_contact,max_dist,max_country)
print("min",min_contact,min_dist,min_country)

