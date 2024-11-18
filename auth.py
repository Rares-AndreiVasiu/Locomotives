from dotenv import load_dotenv
load_dotenv()

import os
from supabase import create_client

from gotrue.errors import AuthApiError

# Load environment variables
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

email = "RaresVasiuClio4@proton.me"
password = "gtasanandreas"

# Sign up user with positional arguments
user = supabase.auth.sign_up(
        { "email": email,
         "password":  password
         }
)

session = None

try:
    session = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password
                }
            )
except AuthApiError as e:
    print("Error: ", e)
except Exception as e:
    print("Unexpected error: e")


print(session)

supabase.auth.sign_out()
