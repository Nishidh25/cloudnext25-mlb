import urllib

import google.auth.transport.requests
import google.oauth2.id_token
import json



def make_authorized_get_request(endpoint,data):
    """
    make_authorized_get_request makes a GET request to the specified HTTP endpoint
    by authenticating with the ID token obtained from the google-auth client library
    using the specified audience value.
    """

    # Cloud Functions uses your function's URL as the `audience` value
    # audience = https://project-region-projectid.cloudfunctions.net/myFunction
    # For Cloud Functions, `endpoint` and `audience` should be equal

    req = urllib.request.Request(endpoint)

    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, endpoint)

    req.add_header("Authorization", f"Bearer {id_token}")
    req.add_header('Content-Type', 'application/json')
    
    response = urllib.request.urlopen(req,data = json.dumps(data).encode('utf-8'))

    return response.read()