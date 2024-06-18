### THIS REPO BELONG TO THE BALLDRAFT

# BallDraft BackEnd API

### Endpoint  and Parameters for Profile

| Endpoints | required parameter(s) | Authorization Required | Authorization Type | request type | example input | example output |
| --------- | ------------------- | -------------- | --------------| -----------| ------------ | ---------- |
| /api/v1/auth/profile/mobile-number/ | mobile_number | Yes | Bearer | PATCH | {"mobile_number": "091...89" }| |
| /api/v1/auth/profile/address/ | address, country, state, city, zip_code | Yes | Bearer | PATCH | {"address": "21, Ola Street","country": "Nigeria","state": "Enugu","city": "NSK","zip_code": "100001"}| |
| /api/v1/auth/update-username/ | user_name | Yes | Bearer | PATCH | {"user_name": "Sparky"} | |

Note: For the profile address endpoint, you can send any individual parameters to make and edit. You must not send all parameter, you can send one or combination of parameter.