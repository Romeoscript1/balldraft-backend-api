class ReferralMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        referral_code = request.GET.get('referral_code')
        if referral_code:
            request.session['referral_code'] = referral_code

        response = self.get_response(request)
        return response
