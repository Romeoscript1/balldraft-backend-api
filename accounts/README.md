### THIS REPO BELONG TO THE BALLDRAFT

# BallDraft BackEnd API

### Endpoint  and Parameters for user authentication

| Endpoints | required parameter(s) | Authorization Required | Authorization Type | request type | example input | example output |
| --------- | ------------------- | -------------- | --------------| -----------| ------------ | ---------- |
| /api/v1/auth/register/ | email, first_name, last_name, dob (year-month-day), password, password2 | No | None | POST | { "email":"example@user.com", "first_name":"example", "last_name":"user", "dob":"2000-02-13","password":"stringst", "confirm_password":"stringst"}| {"data": { "email":user_email, "first_name": user_first_name, "last_name": user_last_name ,"dob": user_date_of_birth},"message": "Welcome test to Balldraft. Thanks for signing up. Check your mail for you passcode."} |
| /api/v1/auth/verify-email/ | otp | No | None | POST | {"otp":"959496"} | {"message":"Account email verified succesfully"} |
| /api/v1/auth/login/ | email, password | No | None | POST | {"email":"example@user.com","password":"lekan2904."} | {'email': user_email,'full_name': user_full_name,'access_token': user_access_token,'refresh_token': user_refresh_token} |
| /api/v1/auth/resend-code/ | email | No | None | POST | {"email":"example@user.com"} | {"message": "New OTP sent successfully"} |
| /api/v1/auth/password-reset/ | email | No | None | POST | {"email":"example@user.com"}| {"message": "An email has been send to you to reset your password"} |
| /api/v1/auth/set-new-password/ | password, confirm_password, uidb64, token| NO | None | PATCH | { "password":"stringst", "confirm_password": "stringst" ,"uidb64": "MQ","token": "c4073u-0...9d2"}| |
| api/v1/auth/logout/ | refresh_token, access_token | Yes | Bearer | POST | {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...jJ9.8dOQQ4sjLkBRGaruWBRZL6-2mO8YjEeKJ-e9VZAgACw","access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...Sg0"} |
| /api/v1/auth/password-reset-confirm/MQ/c4073u-0...9d2/ | None | No | None | None | GET | |
| /api/v1/auth/account/deactivate/ | reason, comment, password | Yes | Bearer | POST | {"reason":"Personal reasons","comment":"I have spent my sch fees","password": "stringst"} | |
| /api/v1/auth/account/activate/ | confirmation | Yes | Bearer | POST | {"confirmation": True} | |
| /api/v1/auth/change-email/ | new_email | Yes | Bearer | PATCH | {"new_email": "user@test.com"} | |