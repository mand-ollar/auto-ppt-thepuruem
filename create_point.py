from pptx import Presentation
from slide_write import slideWrite
from pathlib import Path

import json
import time

beta = 10

global alpha
alpha = 1/beta

complete = True

def type_writer(text: str):
    for seg in text:
        print(seg, end="")
        time.sleep(alpha * 0.02)
    print()

print()

type_writer("Welcome to ThePureum PPT Maker version 1.0.0.\n")
time.sleep(alpha * 0.5)

type_writer("This program is made by 1st year of CCC.")
type_writer("Which stands for,, uh,, Christian Coding Club.(Hope you make new facinating name for this.)")
time.sleep(alpha * 0.5)

type_writer("It makes ppt file from template in any way that you want.(Sequence, conponents, etc.)")
time.sleep(alpha * 0.5)

type_writer("You'll be starting with choosing the template file.\n")
time.sleep(alpha * 0.5)

type_writer("Good Luck!\n")
time.sleep(alpha * 0.5)

print("."); time.sleep(alpha * 0.7)
print("."); time.sleep(alpha * 0.7)
print(".\n"); time.sleep(alpha * 0.7)

type_writer("Select template file...\n")
time.sleep(alpha * 1)

pth = Path.cwd()
pptx_list = list(pth.glob("*.pptx"))
txt_list = list(pth.glob("*.txt"))

for i in range(len(pptx_list)):
    print(f"{i}] {pptx_list[i].name}")
time.sleep(alpha * 0.5)
selection = int(input("\nChoose the number: "))

template_pth = pth/pptx_list[selection]
template = Presentation(template_pth)
time.sleep(alpha * 1)
print()

# get slie layout dictionary {layout_name: layout}
layout_dict = {}
for i in range(len(template.slide_masters)):
    layout_list = template.slide_masters[i].slide_layouts
    for layout in layout_list:
        layout_dict[layout.name] = layout

type_writer("You must make sure that the txt file 'Layout Sequence List' be in this directory with the same name as template file.")
type_writer(f"ex) {template_pth.name[:-5]}.txt\n")
time.sleep(alpha * 1)

print("."); time.sleep(alpha * 0.7)
print("."); time.sleep(alpha * 0.7)
print(".\n"); time.sleep(alpha * 0.7)

if len(txt_list) == 0:
    type_writer("NO TXT FILE...\n")
    time.sleep(alpha * 1)
    selection = 0

else:
    type_writer("Choose the file if you already have on in this directory. If not, just choose 0.\n")
    
    print("0] No matched txt file")
    for i in range(len(txt_list)):
        print(f"{i+1}] {txt_list[i].name}")
    time.sleep(alpha * 0.5)
    selection = input("\nChoose the number: ")
    time.sleep(alpha * 1)
    print()

    while not selection.isdigit():
        type_writer("Please enter a NUMBER.")
        selection = input("\nChoose the number: ")
        time.sleep(alpha * 1)
    selection = int(selection)

if selection == 0:
    type_writer("You don't have the txt file. Go and make one, and come back again.\n")
    time.sleep(alpha * 1)
    
    type_writer("Here's the slide layout list.")
    time.sleep(alpha * 0.5)
    type_writer("Please make sure that the list is based on the exact name of these layouts.\n")
    time.sleep(alpha * 1)
    
    template_slidemasters = template.slide_masters
    print()
    type_writer("[SLIDE LAYOUT LIST]\n")
    
    for slidemaster in template_slidemasters:
        for layout in slidemaster.slide_layouts:
            print(layout.name)
    
    print()
    print()
    time.sleep(alpha * 1)
    type_writer("[4 EXCEPTIONS]\n")
    time.sleep(alpha * 1)
    type_writer("1. Praise and Worship section: You have to write 'praisenworship' to the praise and worship section.")
    time.sleep(alpha * 0.5)
    type_writer("2. Sermon section: You have to write 'allofsermon' to the section from sermon title to the end.")
    time.sleep(alpha * 0.5)
    type_writer("3. After sermon praise section: You have to write 'aftersermon' to the after sermon praise section.")
    time.sleep(alpha * 0.5)
    type_writer("4. Normal praise section: You have to write 'normalpraise' to the normal praise section.")

else:
    with open(f"{txt_list[selection - 1].name}", "r") as txt:
        sequence = txt.read()
        txt.close()
    sequence = sequence.replace(" \n", "")
    sequence_list = sequence.split("\n")

    with open(f"dict/sunday-session.json", "r") as session_json:
        session_dict = json.load(session_json)
        session_json.close()
        
    lyrics_list = []
    for i in range(len(session_dict["title_kr"])):
        song_title = session_dict["title_kr"][i]
        with open(f"lyrics/json/{song_title}.json", "r") as lyrics_json:
            lyrics_list.append(json.load(lyrics_json))
    session_dict["lyrics_list"] = lyrics_list
    
    variable_list = list(session_dict.values())
    slide_writer = slideWrite(template, layout_dict, variable_list)
    
    st = time.time()
    for line in sequence_list:
        if line == "praisenworship":
            no_problem = slide_writer.write_worship()
            if not no_problem:
                complete = False
            
        elif line == "allofsermon":
            slide_writer.write_contents(line)
        
        elif line == "aftersermon":
            slide_writer.write_worship(type="normal", title=variable_list[11])
        
        elif line == "normalpraise":
            slide_writer.write_worship(type="normal", title=variable_list[12])
        
        else:
            slide_writer.write_contents(line)
    
    # save ppt file
    template.save("thepuruem-ppt.pptx")
    type_writer("\nYour PPT is ready!")
    type_writer(f"Saved as 'thepuruem-ppt.pptx'.")
    type_writer(f"Time taken: {round(time.time() - st, 3)}s")
