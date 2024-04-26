def is_float(string):
    if string.replace(".", "").replace(',', '').isnumeric():
        return True
    else:
        return False