import musicbrainzngs as mb
import openpyxl
import excel_table
import json
import sys
from progress.bar import IncrementalBar
from datetime import datetime

workbook = openpyxl.Workbook()
stats_sheet = workbook.create_sheet("Genre statistics")
distr_sheet = workbook.create_sheet("Number of tags distribution")
year_distr_sheet = workbook.create_sheet("Year distribution")
beginning_artist_letter_distr_sheet = workbook.create_sheet("first letter artist dist")
beginning_title_letter_distr_sheet = workbook.create_sheet("first letter title dist")

year_distribution_dict = {}
first_char_title_distr_dict = {}
first_char_artist_distr_dict = {}

def init_config():
    try:
        config_file = open("data_config.json", "r")
        global CONFIG
        CONFIG = json.load(config_file)
        return True
    except IOError as e:
        print(e)
        return False

def album_has_keywords(album_dict):
    if "tag-list" not in album_dict:
        return False

    # if "first-release-date" not in album_dict:
    #     return False

    # if "artist-credit-phrase" not in album_dict:
    #     return False

    # if "title" not in album_dict:
    #     return False
    
    return True

def add_to_distribution(key, distr_dict: dict):
    if key not in distr_dict:
        distr_dict[key] = 0
    distr_dict[key] += 1

def get_data_for_genres(genres, check_for_album_covers):
    mb.set_useragent("test", "0.7.1")
    
    current_row_excel = 1

    for i in range(0, len(genres)):
        current_row_excel += 1

        offset        = 0
        search_tag    = genres[i]
        num_of_covers = int(sys.argv[1])
        MINIMAL_TAG_RATIO = 0.5
        
        #progress bar
        prog_bar = IncrementalBar("Collecting " + '"' + search_tag + '"' + " albums", max=num_of_covers)

        collected_albums = []

        albums_without_cover = 0

        total_tag_count = 0
        search_tag_count = 0
        total_search_tag_in_tag = 0

        last_count = 0

        waited_for_update = False

        search_tag_list = []

        search_tag_containing_list = []

        iters_no_albums_added = 0

        while 0 < num_of_covers:
            result = mb.search_release_groups(query='', limit=100, offset=offset, primarytype="Album", tag=search_tag)
            num_added_albums = 0
            if len(result["release-group-list"]) == 0:
                print("no more albums to collect")
                break
            
            covers = result["release-group-list"]

            for album in covers:

                top_separated_tags = dict()

                if not album_has_keywords(album):
                    continue
                
                tags_in_album = 0
                search_tag_in_album = 0

                is_search_tag_in_album = False

                tags_containing_search_tag_album = 0

                for tag in album["tag-list"]:
                    if int(tag["count"]) < 1:
                        continue    

                    tags_in_album += int(tag["count"])

                    if search_tag == tag["name"]:
                        search_tag_in_album += int(tag["count"])

                    if search_tag in tag["name"]:
                        tags_containing_search_tag_album += int(tag["count"])

                if tags_in_album and MINIMAL_TAG_RATIO < (tags_containing_search_tag_album / tags_in_album):
                    try:
                        if check_for_album_covers:
                            mb.get_release_group_image_list(album["id"])
                    except Exception as err:
                        continue

                    prog_bar.next()
                    total_tag_count += tags_in_album
                    search_tag_count += search_tag_in_album
                    total_search_tag_in_tag += tags_containing_search_tag_album

                    if len(search_tag_containing_list) < tags_containing_search_tag_album:
                        amount_to_append = tags_containing_search_tag_album - len(search_tag_containing_list)
                        search_tag_containing_list.extend([0] * amount_to_append)

                    #add to distributions:
                    if "first-release-date" in album:
                        year = album["first-release-date"].split('-')[0]
                        add_to_distribution(year, year_distribution_dict)

                    if "artist-credit-phrase" in album:
                        artist_letter = album["artist-credit-phrase"][0]
                        add_to_distribution(artist_letter, first_char_artist_distr_dict)

                    if "title" in album:
                        title_letter = album["title"][0]
                        add_to_distribution(title_letter, first_char_title_distr_dict)
                    

                    # print("setting search_tag_containing_list")
                    # print("index:", tags_containing_search_tag_album - 1)
                    search_tag_containing_list[tags_containing_search_tag_album - 1] += 1

                    collected_albums.append(album)
                    num_of_covers -= 1
                    num_added_albums += 1


                if num_of_covers == 0:
                    break
            offset += len(result["release-group-list"])

            if num_added_albums == 0:
                iters_no_albums_added += 1
                # print("iters:", iters_no_albums_added, ", iters before break:", CONFIG["iterations_not_found_albums"])
                if iters_no_albums_added == CONFIG["iterations_not_found_albums"]:
                    # print("no more albums found")
                    break
            else:
                # print("len:", num_added_albums)
                iters_no_albums_added = 0

            last_count = len(collected_albums)

        if (len(distr_sheet["1"]) - 1 < len(search_tag_containing_list)):
            cols_to_append = len(search_tag_containing_list) - (len(distr_sheet["1"]))
            distr_sheet.insert_cols(len(distr_sheet["1"]), cols_to_append)

        stats_sheet.cell(current_row_excel, 1).value = genres[i]
        distr_sheet.cell(current_row_excel, 1).value = genres[i]

        for j in range(0, len(search_tag_containing_list)):
            distr_sheet.cell(current_row_excel, 2 + j).value = search_tag_containing_list[j]
            # distr_sheet.cell(current_row_excel, 2 + j).number_format = "General"

        total_num_covers = len(collected_albums)

        if total_num_covers:
            genre_data = [
                {"total albums": total_num_covers},
                {"total tags in album": total_tag_count},
                {"AVG tags per album": total_tag_count/total_num_covers},
                {"total search tags in albums": search_tag_count},
                {"AVG search tags per album": search_tag_count/total_num_covers},
                {"total tags containing search tag in albums": total_search_tag_in_tag},
                {"AVG tags containing search tag in album": total_search_tag_in_tag/total_num_covers}
            ]
            excel_table.add_genre_stats_to_sheet(stats_sheet, genre_data, current_row_excel)
        else:
            genre_data = [
                {"total albums": 0},
                {"total tags in album": 0},
                {"AVG tags per album": 0},
                {"total search tags in albums": 0},
                {"AVG search tags per album": 0},
                {"total tags containing search tag in albums": 0},
                {"AVG tags containing search tag in album": 0}
            ]
            excel_table.add_genre_stats_to_sheet(stats_sheet, genre_data, current_row_excel)

        # print("tags_containing_search_tag_album list:", search_tag_containing_list)

        print("\n")

    excel_table.add_distribution_to_sheet(year_distr_sheet, sorted(year_distribution_dict.items()), "year", "number of albums")
    excel_table.add_distribution_to_sheet(beginning_artist_letter_distr_sheet, sorted(first_char_artist_distr_dict.items()), "year", "number of albums")
    excel_table.add_distribution_to_sheet(beginning_title_letter_distr_sheet, sorted(first_char_title_distr_dict.items()), "year", "number of albums")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Too few arguments: retrieve_covers.py <num_of_covers>")
        exit(-1)
    
    if not sys.argv[1].isdigit():
        print("Wrong type: <num_of_covers> must be integer")
        exit(-1)

    if not init_config():
        exit(-1)

    excel_table.init_stats_sheet_titles(stats_sheet)
    genres = CONFIG["album_genres"]

    get_data_for_genres(genres, CONFIG["check_for_album_covers"])
    excel_table.add_titles_distribution_sheet(distr_sheet)

    workbook.save("./excel_files/genre_data_1000_50%.xlsx")