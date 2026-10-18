import requests

sentences = [
    "The registration deadline is at the end of the second week.",
    "A first-year student is called a Level 100 student.",
    "Your academic advisor will help you plan your semester.",
    "You must pay your fees before you can register for courses.",
    "Some courses are only offered in the second semester.",
    "An elective is a course that you choose yourself.",
    "A core course is compulsory for every student in the program.",
    "You can repeat a course to improve your grade.",
    "The Department of Computer Science offers many programming courses.",
    "Late registration attracts a penalty fee.",
    "You must attend lectures regularly to pass the course.",
    "Check the student portal for your examination results.",
    "A three-credit course meets for three hours every week.",
    "You should not register for two courses at the same time.",
    "First-year students must attend orientation before registration.",
    "Your final grade depends on your coursework and examination.",
    "You need at least a C grade to pass this course.",
    "Speak to your advisor if you want to change your program.",
    "The semester begins in August and ends in December.",
]

r = requests.post("http://localhost:8000/batch",
                  json={"texts": sentences, "direction": "en2tw"})
data = r.json()["results"]

lines = []
for i, row in enumerate(data, 1):
    block = f"\n[{i}] EN: {row['src']}\n    BASE: {row['base']}\n    FT  : {row['ft']}"
    print(block)
    lines.append(block)

with open("comparison_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("\n\nSaved to comparison_output.txt")