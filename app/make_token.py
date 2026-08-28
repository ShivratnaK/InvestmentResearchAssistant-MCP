import jwt

SECRET = "lksdahfksjbdcfvlkjhagsdvb"  # <-- paste YOUR secret from step 2 here

token = jwt.encode({"sub": "streamlit-client"}, SECRET, algorithm="HS256")
print(token)