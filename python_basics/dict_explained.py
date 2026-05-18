user_dict = {"username": "john","location": "india"}

complex_dict = {
    "username": "john",
    "permissions": ["read","write"],
    "location": "india",
    "roles": {"assigned_roles": ["developer","tester"]}
}
print(complex_dict["roles"]["assigned_roles"][1])