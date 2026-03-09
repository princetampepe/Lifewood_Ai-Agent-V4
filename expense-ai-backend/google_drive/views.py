import os
import json
import tempfile
from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from .models import GoogleDriveToken
from .utils import get_user_drive_credentials

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

SCOPES = ['https://www.googleapis.com/auth/drive']

FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')
OAUTH_REDIRECT_URI = os.environ.get(
    'OAUTH_REDIRECT_URI',
    f'{BACKEND_URL}/api/google/callback/'
)


def _get_client_secrets_file():
    """
    Returns a path to credentials.json.
    On Railway, reads from the GOOGLE_CREDENTIALS_JSON env var and writes a temp file.
    Locally, reads from the repo path set in settings.
    """
    creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if creds_json:
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(json.loads(creds_json), tmp)
        tmp.close()
        return tmp.name
    return settings.GOOGLE_CLIENT_SECRETS


def google_drive_auth(request):
    flow = Flow.from_client_secrets_file(
        _get_client_secrets_file(),
        scopes=SCOPES,
        redirect_uri=OAUTH_REDIRECT_URI,
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
    )
    request.session['state'] = state
    return redirect(authorization_url)


def oauth2callback(request):
    if not request.user.is_authenticated:
        return redirect(f'{BACKEND_URL}/admin/login/')

    flow = Flow.from_client_secrets_file(
        _get_client_secrets_file(),
        scopes=SCOPES,
        redirect_uri=OAUTH_REDIRECT_URI,
    )

    try:
        flow.fetch_token(authorization_response=request.build_absolute_uri())
    except Exception as e:
        print(f"Token fetch failed: {e}")
        return redirect(f'{FRONTEND_URL}?error=auth_failed')

    creds = flow.credentials

    GoogleDriveToken.objects.update_or_create(
        user=request.user,
        defaults={
            'access_token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': ','.join(creds.scopes),
        }
    )

    return redirect(f'{FRONTEND_URL}/drive?status=success')


def list_drive_files(request):
    creds = get_user_drive_credentials(request.user)

    if not creds:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        service = build('drive', 'v3', credentials=creds)

        def get_children(folder_id):
            results = service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id, name, mimeType, size, modifiedTime, webViewLink)",
                pageSize=200,
                orderBy="folder,name"
            ).execute()
            items = results.get('files', [])
            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    item['children'] = get_children(item['id'])
            return items

        folders_result = service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and name contains 'lifewood' and trashed=false",
            fields="files(id, name, mimeType, webViewLink)",
            pageSize=50,
            orderBy="name"
        ).execute()

        lifewood_folders = folders_result.get('files', [])
        for folder in lifewood_folders:
            folder['children'] = get_children(folder['id'])

        return JsonResponse(lifewood_folders, safe=False)

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        if settings.DEBUG:
            return JsonResponse({'error': str(e), 'traceback': tb}, status=500)
        return JsonResponse({'error': 'Internal server error'}, status=500)