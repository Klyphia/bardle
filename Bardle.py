import requests
import time
from bs4 import BeautifulSoup
import re
import random
from student import Student
import json
import os
from flask import Flask, render_template, request


headers = {
    'sec-ch-ua-platform': '"Windows"',
    'If-None-Match': 'W/"1a9t7"',
    'Referer': 'https://bluearchive.wiki/wiki',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/116.0.0.0',
    'sec-ch-ua': '"Opera GX";v="116", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
}

params = {
    'lang': 'en',
    'modules': 'ext.CookieWarning.styles|ext.DarkMode.styles|ext.MobileDetect.nomobile|ext.cite.styles|ext.tabberNeue.init.styles|ext.tmh.player.styles|ext.visualEditor.desktopArticleTarget.noscript|jquery.makeCollapsible.styles|mediawiki.page.gallery.styles|mediawiki.widgets.styles|oojs-ui-core.icons,styles|oojs-ui.styles.indicators|skins.vector.styles.legacy',
    'only': 'styles',
    'skin': 'vector',
}


def get_all_characters_table_soup() -> BeautifulSoup:
    response = requests.get("https://bluearchive.wiki/wiki/Characters", params=params, headers=headers)
    character_table_soup = BeautifulSoup(response.text, "html.parser")
    character_table = character_table_soup.find("tbody")
    character_list = character_table.find_all("tr")

    return character_list

def get_random_character(character_list: list) -> BeautifulSoup:
    random_index = random.randint(1, len(character_list) - 1)
    random_character = character_list[random_index]
    character_page = requests.get("https://bluearchive.wiki"  + random_character.a['href'], params=params, headers=headers)
    character_page_soup: BeautifulSoup = BeautifulSoup(character_page.text, "html.parser")

    return(character_page_soup)



def get_random_student_name(soup: BeautifulSoup) -> str:
    test = soup.find(class_="mw-page-title-main")
    return(test.string)

def get_random_student_school(soup: BeautifulSoup) -> str:
    wikitable_table = soup.find(class_="wikitable")
    wikitable_rows = wikitable_table.find_all("tr")
    school_name = wikitable_rows[3].img['alt']

    return school_name
          


def get_ex_skill_cost(soup: BeautifulSoup) -> str:
    ex_skill_table = soup.find(class_="skilltable")
    table_skill_costs = ex_skill_table.find_all("td", attrs={"rowspan": ["1", "2", "3", "4","5"]})
    highest_cost = table_skill_costs[len(table_skill_costs) - 1]
    ex_skill_cost = highest_cost.contents[0]

    return(ex_skill_cost.string.strip())


def get_school_image(soup: BeautifulSoup) -> str:
    image_row = soup[3]
    images_list = image_row.find("span").find_all("img")
    school_logo_link = images_list[len(images_list) - 1]['srcset']

    return(school_logo_link.split()[2])


def get_attack_type(soup:BeautifulSoup) -> str:
    attack_type_row = soup[4]
    attack_type = attack_type_row.td.string

    return(attack_type)


def get_student_age(soup: BeautifulSoup) -> str:
    student_age_row = soup[11]
    age = student_age_row.td.string
    
    return(age)


def get_student_height(soup: BeautifulSoup) -> str:
    student_height_row = soup[13]
    height = student_height_row.td.string

    return height

def get_student_release_date(soup: BeautifulSoup) -> str:
    student_release_date_row = soup[18]
    release_date = student_release_date_row.td.string

    return release_date

def get_student_weapon_type(soup: BeautifulSoup) -> str:
    student_weapon_row = soup[8]
    weapon_class = student_weapon_row.find(class_="weapon-text")

    return weapon_class.contents[1]

def get_student_role(soup: BeautifulSoup) -> str:
    student_role_row = soup[3]
    table_data = student_role_row.find_all("td")
    position_role = table_data[1].contents[2].strip().split('/')[0]

    return position_role

def get_student_icon(student_page_soup: BeautifulSoup) -> str:
    # Assuming that the student icon is located in a <figure> element.
    figure_tag = student_page_soup.find("figure")
    if figure_tag and figure_tag.img and 'srcset' in figure_tag.img.attrs:
        # Split the srcset and pick a higher resolution option.
        srcset = figure_tag.img['srcset']
        # For example, picking the last URL in the srcset (highest resolution)
        srcset_entries = srcset.split(',')
        high_res_entry = srcset_entries[-1].strip()  # e.g. "https://... 2x"
        # Get the URL portion (first token)
        high_res_url = high_res_entry.split(' ')[0]
        return high_res_url
    # Fallback to empty string if something goes wrong.
    return ""

# only rerun this function when new characters are added. To update the student_icons.json file
def write_student_icons_to_json(character_list: list, filename: str = "student_icons.json"):
    student_icons_dict = {}  # Dictionary to store base name → icon mapping

    for character_soup in character_list[1:]:  # Skip header row
        student_link_tag = character_soup.find_next("a")
        character_name = student_link_tag['title']
        # Extract base name (before any parentheses)
        base_name = character_name.split(" (")[0]
        
        # Skip excluded characters
        if base_name in {"Hatsune Miku", "Misaka Mikoto", "Saten Ruiko", "Shokuhou Misaki"}:
            continue

        if base_name not in student_icons_dict:
            # Construct the URL to the student's page
            student_page_url = "https://bluearchive.wiki" + student_link_tag['href']
            response = requests.get(student_page_url, params=params, headers=headers)
            student_page_soup = BeautifulSoup(response.text, "html.parser")
            
            # Use your get_student_icon() function to get the high-res icon URL
            student_icon = get_student_icon(student_page_soup)
            student_icons_dict[base_name] = student_icon

    # Write the dictionary to a JSON file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(student_icons_dict, f, indent=4)

    print(f"Student icons successfully written to {filename}")


def set_full_random_student_info(student_icon: str, 
                school_icon: str, 
                damage_type: str,
                student_role: str, 
                ex_skill_cost: str, 
                weapon_type: str,
                student_height: str, 
                student_release_date: str) -> Student:
    
    student_object = Student(student_icon, 
                school_icon, 
                damage_type,
                student_role, 
                ex_skill_cost, 
                weapon_type,
                student_height, 
                student_release_date)
    
    return student_object
    

def get_random_character_unique_weapon(soup: BeautifulSoup) -> str:
    character_weapon_table = soup.find(class_="wikitable weapontable")
    character_weapon_image = character_weapon_table.find("img")

    return(character_weapon_image['src'])

def get_random_character_voice_line_1(soup: BeautifulSoup) -> str:
    character_name = get_random_student_name(soup)
    response = requests.get("https://bluearchive.wiki/wiki/" + character_name + "/audio", params = params, headers=headers)
    character_audio_soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
    character_source_tag = character_audio_soup.find_all("audio")
    character_intro_voice_line = character_source_tag[7]
    character_audio_link = character_intro_voice_line.find("source").get("src")

    return(character_audio_link)

def get_random_character_voice_line_2(soup: BeautifulSoup) -> str:
    character_name = get_random_student_name(soup)
    response = requests.get("https://bluearchive.wiki/wiki/" + character_name + "/audio", params = params, headers=headers)
    character_audio_soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
    character_source_tag = character_audio_soup.find_all("audio")
    character_intro_voice_line = character_source_tag[1]
    character_audio_link = character_intro_voice_line.find("source").get("src")

    return(character_audio_link)

def get_random_song_ost_tag() -> str:
    response = requests.get("https://bluearchive.wiki/wiki/Music", params = params, headers=headers)
    audio_page_soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
    audio_tags_list = audio_page_soup.find_all(class_="track-standalone")
    random_index = random.randint(1, len(audio_tags_list) - 1)
    random_ost_tag = audio_tags_list[random_index]

    return(random_ost_tag)

def get_random_ost_name(soup: BeautifulSoup) -> str:
    song_title = soup.find(class_="title").string

    return(song_title)

def get_random_ost_link(soup: BeautifulSoup) -> str:
    ost_link = soup.find("source").get("src")

    return(ost_link)


def get_random_ost_producer(soup: BeautifulSoup) ->str:
    song_producer = soup.find(class_="artist").string
    
    return(song_producer)

def get_random_ost_track_number(soup: BeautifulSoup) -> str:
    track_number = soup.find(class_="id").string

    return track_number


def get_list_of_all_student_names(soup: BeautifulSoup) -> list:
    
    full_student_list = set()  # Using a set to store unique names

    for character_soup in soup:
        character_name = character_soup.find_next("a")['title']
        
        # Extract base name (split at first ' (')
        base_name = character_name.split(" (")[0]
        
        full_student_list.add(base_name)  # Add only the base name
    
    # Define the names to be removed
    excluded_names = {"Hatsune Miku", "Misaka Mikoto", "Saten Ruiko", "Shokuhou Misaki"}
    
    # Remove the excluded names
    cleaned_list = sorted(full_student_list - excluded_names)

    return sorted(cleaned_list)  # Return a sorted list for consistency

def get_list_of_all_student_images(character_list: list) -> list:
    student_icons_dict = {}  # Dictionary to store base name → icon mapping

    for character_soup in character_list[1:]:  # Skip header row
        # Get the student name from the <a> tag
        student_link_tag = character_soup.find_next("a")
        character_name = student_link_tag['title']
        # Extract base name (before any parentheses)
        base_name = character_name.split(" (")[0]
        
        # Skip excluded characters
        if base_name in {"Hatsune Miku", "Misaka Mikoto", "Saten Ruiko", "Shokuhou Misaki"}:
            continue

        if base_name not in student_icons_dict:
            # Build the URL for the student's detail page.
            student_page_url = "https://bluearchive.wiki" + student_link_tag['href']
            response = requests.get(student_page_url, params=params, headers=headers)
            student_page_soup = BeautifulSoup(response.text, "html.parser")
            
            # Use the get_student_icon function to get the high-res icon.
            student_icon = get_student_icon(student_page_soup)
            student_icons_dict[base_name] = student_icon

    # Return the icons sorted by student name.
    sorted_icons = [student_icons_dict[name] for name in sorted(student_icons_dict)]
    return sorted_icons


def write_song_info_to_json(filename: str = "song_info.json"):
    response = requests.get("https://bluearchive.wiki/wiki/Music", params=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all song entries (each song entry is assumed to have the class "track-standalone")
    track_tags = soup.find_all(class_="track-standalone")
    print(f"Found {len(track_tags)} track-standalone elements")
    
    songs = []
    for track in track_tags:
        # Extract the song title (or use empty string if not found)
        title_elem = track.find(class_="title")
        title = title_elem.string.strip() if title_elem and title_elem.string else ""
        
        # Extract the producer (artist); default to "Unknown" if not found.
        producer_elem = track.find(class_="artist")
        producer = producer_elem.string.strip() if producer_elem and producer_elem.string else "Unknown"
        
        # Extract the track number from the element with class "id"; if missing or invalid, use 9999.
        track_num_elem = track.find(class_="id")
        if track_num_elem and track_num_elem.string:
            try:
                track_number = int(track_num_elem.string.strip())
            except ValueError:
                track_number = 9999
        else:
            track_number = 9999
        
        # Extract the audio file link from an <audio> element.
        audio_elem = track.find("audio")
        if audio_elem:
            source_elem = audio_elem.find("source")
            audio_link = source_elem["src"] if source_elem and source_elem.has_attr("src") else ""
        else:
            audio_link = ""
        
        songs.append({
            "track_number": track_number,
            "title": title,
            "producer": producer,
            "audio_link": audio_link
        })
    
    # Sort the songs by track number.
    songs.sort(key=lambda x: x["track_number"])
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(songs, f, indent=4)
    
    print(f"Song info successfully written to {filename}")







app = Flask(__name__)
characters_table_soup = get_all_characters_table_soup()
full_student_list = get_list_of_all_student_names(characters_table_soup)

@app.route('/')
def index():
    soup = get_random_character(characters_table_soup)
    student_name = get_random_student_name(soup).split(' ', 1)[0]
    character_weapon_url = get_random_character_unique_weapon(soup)
    with open("student_icons.json", "r", encoding="utf-8") as f:
        student_icons = json.load(f)
    return render_template('index.html',
                           character_weapon_url=character_weapon_url,
                           student_name=student_name,
                           student_icons=student_icons)


@app.route('/song_guess')
def song_guess():
    ost_soup = get_random_song_ost_tag()
    song_title = get_random_ost_name(ost_soup)

    while song_title.split(' ', 1)[0] == "Theme":
        ost_soup = get_random_song_ost_tag()
        song_title = get_random_ost_name(ost_soup)

    song_link = get_random_ost_link(ost_soup)
    song_producer = get_random_ost_producer(ost_soup)
    song_track_number = get_random_ost_track_number(ost_soup)

    # Load song titles from your JSON file
    with open("song_titles.json", "r", encoding="utf-8") as f:
        song_titles = json.load(f)

    print(song_link)
    print(song_title)

    return render_template('song_guess.html', 
                           song_title=song_title, 
                           song_link=song_link, 
                           full_student_list=full_student_list, 
                           song_producer=song_producer, 
                           song_track_number=song_track_number,
                           song_titles=song_titles)


@app.route('/voice_guess')
def voice_guess():
    excluded_names = {"Hatsune Miku", "Misaka Mikoto", "Saten Ruiko", "Shokuhou Misaki"}
    soup = get_random_character(characters_table_soup)
    student_name = get_random_student_name(soup)
    base_name = student_name.split(" (")[0].strip()
    while base_name in excluded_names:
        soup = get_random_character(characters_table_soup)
        student_name = get_random_student_name(soup)
        base_name = student_name.split(" (")[0].strip()
        
    character_voice_link_1 = get_random_character_voice_line_1(soup)
    character_voice_link_2 = get_random_character_voice_line_2(soup)
    student_school = get_random_student_school(soup)
    with open("student_icons.json", "r", encoding="utf-8") as f:
        student_icons = json.load(f)
    return render_template('voice_guess.html',
                           character_voice_link_1=character_voice_link_1,
                           character_voice_link_2=character_voice_link_2,
                           student_name=student_name,
                           full_student_list=full_student_list,
                           student_icons=student_icons,
                           student_school=student_school)

    

@app.route('/bardle')
def bardle():
    with open("student_icons.json", "r", encoding="utf-8") as f:
        student_icons = json.load(f)
    return render_template('bardle.html', student_icons=student_icons)




if __name__ == '__main__':
    app.run()
    # soup = get_random_character()
    # character_profile_table = soup.find(class_="wikitable character")
    # character_profile_rows = character_profile_table.tbody.find_all("tr",recursive=False)
    # print(get_student_age(character_profile_rows))
    # print(get_attack_type(character_profile_rows))
    # print(get_school_image(character_profile_rows))
    # print(get_student_height(character_profile_rows))
    # print(get_student_release_date(character_profile_rows))
    # print(get_student_weapon_type(character_profile_rows))
    # print(get_student_role(character_profile_rows))
    # print(get_student_icon(character_profile_rows))
    # print(get_random_student_name(soup))
    # print(get_ex_skill_cost(soup))

    # print(get_random_character_unique_weapon(soup))
    
    

