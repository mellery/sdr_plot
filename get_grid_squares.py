import csv
import maidenhead as mh

grid_list = []

with open('contacts_latlon.txt') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        lat = float(row[1])
        lon = float(row[2])
        level = 4
        grid = mh.toMaiden(lat,lon)[0:4]
        if grid not in grid_list:
            grid_list.append(grid)

print(grid_list)
with open('seen_grids.txt', 'w') as f:
    for item in grid_list:
        f.write("%s\n" % item)
