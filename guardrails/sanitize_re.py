import re 

USER_INPUT = """
Hi, my name is Aryan.
My email is xxxx. 
My phone number is xxxx.

Please draft an email to my boss requesting
for a 10 days PTO.
"""

santized_output = re.sub(r"\w+@\w+\.\w+","<REDACTED_EMAIL_ADDRESS>",USER_INPUT)
print(santized_output)