import os, requests
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from django.conf import settings

class InstagramOAuthView(View):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return HttpResponseBadRequest("Missing code")
        # Exchange for token
        resp = requests.post(
            'https://api.instagram.com/oauth/access_token',
            data={
                'client_id':     settings.INSTAGRAM_APP_ID,
                'client_secret': settings.INSTAGRAM_APP_SECRET,
                'grant_type':    'authorization_code',
                'redirect_uri':  settings.INSTAGRAM_REDIRECT_URI,
                'code':          code,
            }
        )
        data = resp.json()
        long_token = data['access_token']
        ig_id       = data['user_id']
        # Save these somewhere: .env, DB, etc.
        # Then subscribe the IG account to messages:
        requests.post(
            f'https://graph.facebook.com/v15.0/{ig_id}/subscribed_apps',
            params={
                'access_token': long_token,
                'subscribed_fields': 'messages'
            }
        )
        return redirect('/admin/')  # or wherever

