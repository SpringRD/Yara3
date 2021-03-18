import codecs
import re
import time
import datetime


def clean_srt(source, destination):
    f_in = codecs.open(source, 'r', "utf_8")
    f_out = codecs.open(destination, 'w', "utf_8")

    for line in f_in:
        match1 = re.match('^[0-9]+\s$', line)
        match2 = re.match('^\s$', line)
        match3 = re.match('^[0-9]{2}:', line)
        match4 = re.match('^﻿', line)

        if not (match1 or match2 or match3 or match4):
            f_out.write(line)
    f_in.close()
    f_out.close()

    print('finish cleaning')


def clean(source):
    lines = []
    f_in = codecs.open(source, 'r', "utf_8")
    count = 0
    for line in f_in:
        match1 = re.match('^[0-9]+\s$', line)
        match2 = re.match('^\s$', line)
        match3 = re.match('^[0-9]{2}:', line)
        match4 = re.match('^﻿', line)

        if not (match1 or match2 or match3 or match4):
            lines.append(line)
            count += 1
    f_in.close()
    print('finish cleaning')
    return lines, count


def get_regions(source):
    file = codecs.open(source, 'r', "utf_8")

    regions = []
    for line in file:
        line_match = re.match('^[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}', line)
        if line_match:
            my_line = re.findall('[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}', line)
            x = time.strptime(my_line[0].split(',')[0], '%H:%M:%S')
            start_time = datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec,
                                            milliseconds=int(my_line[0].split(',')[1])).total_seconds()
            y = time.strptime(my_line[1].split(',')[0], '%H:%M:%S')
            end_time = datetime.timedelta(hours=y.tm_hour, minutes=y.tm_min, seconds=y.tm_sec,
                                          milliseconds=int(my_line[1].split(',')[1])).total_seconds()

            start = max(0.0, start_time - 0.25)
            end = end_time + 0.25

            elapsed_time = float('{0:.3f}'.format(end - start))

            regions.append((start_time, elapsed_time))
    return regions

