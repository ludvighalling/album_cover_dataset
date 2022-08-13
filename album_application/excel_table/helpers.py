import openpyxl

def init_stats_sheet_titles(sheet):
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

def add_titles_distribution_sheet(distr_sheet):
    distr_sheet.cell(1, 1).value = "genre"
    for i in range(1, len(distr_sheet["1"])):
        distr_sheet.cell(1, i + 1).value = i

def add_genre_stats_to_sheet(sheet, data, row):
    for i in range(0, len(data)):
        col = len(sheet["1"]) - i
        # print("values:", data[i].values())
        sheet.cell(row, col).value = list(data[i].values())[0]
        sheet.cell(1, col).value = list(data[i].keys())[0]

def add_year_disribution_to_sheet(sheet, year_distribution_dict):
    sheet.cell(1, 1).value = "year"
    sheet.cell(1, 2).value = "number of albums"
    current_row = 2

    for year, amount in year_distribution_dict:
        sheet.cell(current_row, 1).value = year
        sheet.cell(current_row, 2).value = amount
        current_row += 1

def add_distribution_to_sheet(sheet, distr_dict: dict, key_title: str, number_title: str):
    sheet.cell(1, 1).value = key_title
    sheet.cell(1, 2).value = number_title
    current_row = 2

    for key, value in distr_dict:
        sheet.cell(current_row, 1).value = key
        sheet.cell(current_row, 2).value = value
        current_row += 1