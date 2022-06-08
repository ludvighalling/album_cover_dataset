import openpyxl

def init_sheet_titles(sheet):
    if type(sheet) is not openpyxl.worksheet.worksheet.Worksheet:
        return False
    
    sheet["A1"] = "genre"
    sheet["B1"] = "total albums"
    sheet["C1"] = "total tags in album"
    sheet["D1"] = "AVG tags per album"
    sheet["E1"] = "total search tag in album"
    sheet["F1"] = "AVG search tag in album"
    sheet["G1"] = "total tags containing search tag"
    sheet["H1"] = "AVG tags containing search tag"

    return True

def add_genre_stats_to_sheet(sheet, data, row):
    for i in range(0, len(data)):
        col = len(sheet["1"]) - i
        # print("values:", data[i].values())
        sheet.cell(row, col).value = str(list(data[i].values())[0])
        sheet.cell(1, col).value = str(list(data[i].keys())[0])