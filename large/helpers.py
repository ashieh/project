import csv

"""
CSV reader helper function
Takes in a file name, opens the file,
and returns a list of csv rows
"""
def read_csv(file_name):

    lines = []
    with open(file_name, 'rb') as csvfile:
        reader = csv.reader(csvfile)

        # Skip Header
        next(reader, None)
        for row in reader:
            lines.append(row)

    return lines


"""
CSV writer helper function
Takes in a file name, headers, and a dictionary for the rows
and writes the results to the given file. Assumes each row is only
2 columns.
"""

def write_csv(file_name, headers, rows):

    with open(file_name, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for val1, val2 in rows.iteritems():
            writer.writerow([val1, val2])


