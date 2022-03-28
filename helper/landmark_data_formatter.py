# Help to create landmarks with areas.

import csv
import random

area_rows = []
with open('areas.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            # read rows.
            area_rows.append(row)
            print(row)
            # line_count += 1

print(area_rows)

with open('landmarks.csv', mode='w') as landmark_file:
    landmark_writer = csv.writer(
        landmark_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for area_row in area_rows:
        for i in range(1, 3):
            rand_lat = str(round(random.uniform(1.283920, 1.414346), 6))
            rand_lng = str(round(random.uniform(103.763548, 103.878083), 6))

            landmark_writer.writerow(
                [area_row[0], area_row[1] + str(i), rand_lat, rand_lng, 3])
        # employee_writer.writerow(['Erica Meyers', 'IT', 'March'])

# print(f'Processed {line_count} lines.')

# for area in area_statements.getAllAreas(database_client):
#     for i in range(1, 3):
#         rand_lat = str(round(random.uniform(1.283920, 1.414346), 6))
#         rand_lng = str(round(random.uniform(103.763548, 103.878083), 6))
#         landmark_data.append(
#             (area[0], area[1] + ' landmark ' + str(i), rand_lat, rand_lng))
