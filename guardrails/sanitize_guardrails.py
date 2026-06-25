from guardrails.hub import DetectPII
from guardrails import Guard

guard = Guard().use(
    DetectPII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER"], on_fail="fix")
)

USER_INPUT = """
Hi, my name is Aryan.
My email is xxxx. 
My phone number is xxx.

Please draft an email to my boss requesting
for a 10 days PTO.
"""

try:
    result = guard.validate(USER_INPUT)
    print(result)
except Exception as e:
    print(f"Error: {e}")