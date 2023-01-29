def name_filter(line, start, end):
    result = []
    if start <= line[3][0] <= end:
        result = line
    return result