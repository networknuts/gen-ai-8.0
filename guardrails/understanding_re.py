import re 

USER_DATA = """
john <john@networknuts.net>
jane <jane@networknuts.net>
arthur <arthur@networknuts.net>
thomas <thomas@networknuts.net>
chris <chris@networknuts.net>
bobbi <bobbi@networknuts.net>
"""

#bobby, bobbi, robbi, robby
match_one = re.search(r"[r,b]obb[y,i]",USER_DATA)

#chr??
match_two = re.search(r"chr[a-z][a-z]",USER_DATA)

#art________
match_three = re.search(r"art[a-z]+",USER_DATA)

#th????
match_four = re.search(r"th[a-z]{4}",USER_DATA)

#email address matching - first available match
email_match = re.search(r"[a-zA-Z0-9_]+@[a-zA-Z0-9_]+\.[a-zA-Z0-9]+",USER_DATA)

#all email matches
email_matches = re.findall(r"[a-zA-Z0-9_]+@[a-zA-Z0-9_]+\.[a-zA-Z0-9]+",USER_DATA)

#expression shortcut
email_matches_shortcut = re.findall(r"\w+@\w+\.\w+",USER_DATA)
print(email_matches_shortcut)