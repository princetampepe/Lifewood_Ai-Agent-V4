# google_drive/utils.py
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from .models import GoogleDriveToken

def get_user_drive_credentials(user):
    """
    Retrieves credentials safely. Falls back to the first available 
    token if the user is not logged in (common in local dev).
    """
    token_record = None

    try:
        # 1. Try to get the specific user's token if they are logged in
        if user and user.is_authenticated:
            token_record = GoogleDriveToken.objects.filter(user=user).first()
        
        # 2. Fallback: If no user or anonymous, grab the first token in the DB
        # This is what allows Next.js to work during local testing!
        if not token_record:
            token_record = GoogleDriveToken.objects.first()

        if not token_record:
            print("No GoogleDriveToken found in database.")
            return None

        # 3. Build the Credentials object
        creds = Credentials(
            token=token_record.access_token,
            refresh_token=token_record.refresh_token,
            token_uri=token_record.token_uri,
            client_id=token_record.client_id,
            client_secret=token_record.client_secret,
            scopes=token_record.scopes.split(',')
        )

        # 4. Handle Expiration
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_record.access_token = creds.token
            token_record.save()

        return creds

    except Exception as e:
        print(f"Error in get_user_drive_credentials: {e}")
        return None