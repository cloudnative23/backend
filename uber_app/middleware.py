from uber_app.models import Account

class UserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        user = None
        if user_id := request.session.get("user", default=None):
            # Get the Account instance
            try:
                user = Account.objects.get(pk=user_id)
            except Account.DoesNotExist:
                request.session['user'] = None
                pass

        request.user = user
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
