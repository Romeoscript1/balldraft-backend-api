### THIS REPO BELONG TO THE BALLDRAFT

# BallDraft BackEnd API

### Endpoint  and Parameters

| Endpoints | required parameter(s) | example output |
| --------- | ------------------- | -------------- | 
| /api/v1/auth/register/ | email, first_name, last_name, dob (year-month-day), password, password2 | {"data": { "email":user_email, "first_name": user_first_name, "last_name": user_last_name ,"dob": user_date_of_birth},"message": "Welcome test to Balldraft. Thanks for signing up. Check your mail for you passcode."} |
| /api/v1/auth/verify-email/ | otp | {"message":"Account email verified succesfully"} |
| /api/v1/auth/login/ | email, password | {'email': user_email,'full_name': user_full_name,'access_token': user_access_token,'refresh_token': user_refresh_token} |
