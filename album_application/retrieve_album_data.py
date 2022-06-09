import musicbrainzngs as mb
import openpyxl
import excel_table
import json
import sys
from progress.bar import IncrementalBar

workbook = openpyxl.Workbook()
sheet1 = workbook.create_sheet("Genre statistics")
sheet2 = workbook.create_sheet("Number of tags distribution")

def get_data_for_genres(genres, check_for_album_covers):
    mb.set_useragent("test", "0.7.1")

    if len(sys.argv) < 2:
        print("Too few arguments: retrieve_covers.py <num_of_covers>")
        return -1
    
    if not sys.argv[1].isdigit():
        print("Wrong type: <num_of_covers> must be integer")
        return -1
    
    current_row_excel = 1

    for i in range(0, len(genres)):
        current_row_excel += 1

        offset        = 0
        search_tag    = genres[i]
        num_of_covers = int(sys.argv[1])
        tag_ratio = 0.5
        
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

        while 0 < num_of_covers:
            result = mb.search_release_groups(query='', limit=100, offset=offset, primarytype="Album", tag=search_tag)
            covers = result["release-group-list"]
            
            for album in covers:

                top_separated_tags = dict()

                if "tag-list" not in album:
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

                if tags_in_album and tag_ratio < (tags_containing_search_tag_album / tags_in_album):
                    try:
                        if check_for_album_covers:
                            mb.get_release_group_image_list(album["id"])

                        prog_bar.next()
                        total_tag_count += tags_in_album
                        search_tag_count += search_tag_in_album
                        total_search_tag_in_tag += tags_containing_search_tag_album

                        if len(search_tag_containing_list) < tags_containing_search_tag_album:
                            # print("search_tag_containing_list len:", len(search_tag_containing_list))
                            # print("tags_containing_search_tag_album:", tags_containing_search_tag_album)
                            amount_to_append = tags_containing_search_tag_album - len(search_tag_containing_list)
                            search_tag_containing_list.extend([0] * amount_to_append)

                        # print("setting search_tag_containing_list")
                        # print("index:", tags_containing_search_tag_album - 1)
                        search_tag_containing_list[tags_containing_search_tag_album - 1] += 1

                        collected_albums.append(album)
                        num_of_covers -= 1
                    except Exception as err:
                        pass

                if num_of_covers == 0:
                    break
            offset += len(result["release-group-list"])

            last_count = len(collected_albums)

        if (len(sheet2["1"]) - 8 < len(search_tag_containing_list)):
            cols_to_append = len(search_tag_containing_list) - (len(sheet2["1"]) - 8)
            sheet2.insert_cols(len(sheet2["1"]) - 6, cols_to_append)

        sheet1.cell(current_row_excel, 1).value = genres[i]
        sheet2.cell(current_row_excel, 1).value = genres[i]

        for j in range(0, len(search_tag_containing_list)):
            sheet2.cell(current_row_excel, 2 + j).value = search_tag_containing_list[j]
            # sheet2.cell(current_row_excel, 2 + j).number_format = "General"

        total_num_covers = len(collected_albums)

        genre_data = [
            {"total albums": total_num_covers},
            {"total tags in album": total_tag_count},
            {"AVG tags per album": total_tag_count/total_num_covers},
            {"total search tags in albums": search_tag_count},
            {"AVG search tags per album": search_tag_count/total_num_covers},
            {"total tags containing search tag in albums": total_search_tag_in_tag},
            {"AVG tags containing search tag in album": total_search_tag_in_tag/total_num_covers}
        ]

        excel_table.add_genre_stats_to_sheet(sheet1, genre_data, current_row_excel)

        print("\n")


if __name__ == "__main__":
    excel_table.init_stats_sheet_titles(sheet1)

    try:
        config_file = open("data_config.json", "r")
        config: dict = json.load(config_file)

    except IOError as e:
        print(e)
        exit(-1)

    genres = config["album_genres"]

    get_data_for_genres(genres, config["check_for_album_covers"])
    excel_table.add_titles_distribution_sheet(sheet2)

    workbook.save("./excel_files/genre_data.xlsx")