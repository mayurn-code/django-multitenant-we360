import requests
from django.conf import settings
from requests.exceptions import ConnectionError
import jwt
import datetime


class KeyCloakConnection:

    @staticmethod
    def check_connection():
        try:
            url = f"{settings.KEYCLOAK_URL}realms/master/protocol/openid-connect/token"
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            payload = {"client_id": settings.KEYCLOAK_CLIENT_ID,
                       "client_secret": settings.KEYCLOAK_CLIENT_SECRET, "grant_type": settings.KEYCLOAK_GRANT_TYPE}
            result = requests.post(url, data=payload, headers=headers)
            if result.status_code == 200:
                context = {
                    'status': True,
                    'access_token': result.json()['access_token']
                }
            else:
                context = {
                    'status': False
                }
        except ConnectionError:
            context = {
                'status': False
            }
        return context

    def check_user(self, request):
        data = self.check_connection()
        status = False
        if data['status']:
            url = f"{settings.KEYCLOAK_URL}admin/realms/{settings.KEYCLOAK_REALM}/users/?username={request.user.username}"
            headers = {
                'Authorization': f'Bearer {data["access_token"]}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            result = requests.get(url, headers=headers)
            if result.status_code == 200:
                data = result.json()
                if len(data) == 1:
                    # you can send your role or any other retrun data using dict
                    status = True
        return status

    def get_user_details(self, username):
        try:
            data = self.check_connection()
            if data['status']:
                url = f"{settings.KEYCLOAK_URL}admin/realms/{settings.KEYCLOAK_REALM}/users/"
                headers = {
                    'Authorization': f'Bearer {data["access_token"]}',
                }

                url = f"{settings.KEYCLOAK_URL}admin/realms/{settings.KEYCLOAK_REALM}/users/?username={username}"
                getuser = requests.get(url, headers=headers)

                if getuser.status_code == 200:
                    userdata = getuser.json()
                    userdata = userdata[0]
                    data = {
                        "id": userdata["id"],
                        "username": userdata["username"],
                        "email": userdata["email"]
                    }
                    return {
                        "data": data,
                        "message": "User details found"
                    }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

    def send_email(self, userdetails):
        userdata = userdetails['data']

        try:
            data = self.check_connection()

            if data['status']:
                url = f"{settings.KEYCLOAK_URL}admin/realms/{settings.KEYCLOAK_REALM}/users/{userdata['id']}/send-verify-email"
                headers = {
                    'Authorization': f'Bearer {data["access_token"]}',
                }
                response = requests.put(url, headers=headers)
                if response.status_code == 500:
                    return False
                if response.status_code >= 200 and response.status_code < 300:
                    return True
        except Exception as e:
            print("From send email", str(e))
            return False

    def create_user(self, username, email, firstName, lastName, password_value=None):
        data = self.check_connection()

        if data['status']:
            url = f"{settings.KEYCLOAK_URL}admin/realms/{settings.KEYCLOAK_REALM}/users/"
            headers = {
                'Authorization': f'Bearer {data["access_token"]}',
            }
            ct = datetime.datetime.now()

            timestamp = ct.timestamp()
            payload = {
                "enabled": True,
                "createdTimestamp": timestamp,
                "username": username,
                "email": email,
                "emailVerified": False,
                "firstName": firstName,
                "lastName": lastName,
                "credentials": [
                    {
                        "type": "password",
                        "value": password_value,
                        "temporary": False
                    }
                ],
                "realmRoles": ["owner"],
                "requiredActions": [],
                "attributes": {"user_type":"Admin"}
            }
            result = requests.post(url, json=payload, headers=headers)

            if result.status_code == 201:
                user = KeyCloakConnection.get_user_details(self, username)
                user_data = user['data']
                return {
                    "data":user_data,
                    "status": True,
                    "message": "User created successfully"
                }
            elif result.status_code == 409:
                result_json = result.json()
                return {
                    "status": False,
                    "message": result_json["errorMessage"]
                }
            else:

                return {
                    "status": False,
                    "message": "Something went wrong, please try again"
                }

    def update_user_email_verify_details(self, user_id):
        data = self.check_connection()

        if data['status']:
            url = url = f"{settings.KEYCLOAK_URL}admin/realms/{settings.KEYCLOAK_REALM}/users/{user_id}"
            headers = {
                'Authorization': f'Bearer {data["access_token"]}',
            }

            payload = {
                "id": user_id,
                # "createdTimestamp": timestamp,
                "username": "Superman",
                "enabled": True,
                "totp": False,
                "emailVerified": True
            }

            result = requests.put(url, json=payload, headers=headers)
            print(result, "update_user_email_verify_details")
            if result.status_code >= 200 and result.status_code < 300:
                return {
                    "success": True,
                    "status": result.status_code,
                    "message": "Successfully updated"
                }
            else:
                return {
                    "success": False,
                    "status": 500,
                    "message": "Something missing"
                }

    def create_client(self, unique_uuid, clientname):
        data = self.check_connection()

        if data['status']:
            url = f"{settings.KEYCLOAK_URL}admin/realms/{settings.KEYCLOAK_REALM}/clients"
            headers = {
                'Authorization': f'Bearer {data["access_token"]}',
            }
            payload = {
                "clientId": unique_uuid,
                "name": clientname,
                "access": {
                    "view": True,
                    "configure": True,
                    "manage": True
                },
                "authorizationServicesEnabled": False,
                "bearerOnly": False,
                "directAccessGrantsEnabled": True,
                "enabled": True,
                "protocol": "openid-connect",
                "description": "rest-api",
                "clientAuthenticatorType": "client-secret",
                "defaultRoles": [
                    "manage-account",
                    "view-profile"
                ],
                "redirectUris": [
                    f"/realms/{settings.KEYCLOAK_REALM}/account/"
                ],

            }
            result = requests.post(url, json=payload, headers=headers)

            if result.status_code >= 200 and result.status_code < 300:
                return {
                    "status": True,
                    "message": "Client created successfully"
                }
            elif result.status_code == 409:
                result_json = result.json()

                return {
                    "status": False,
                    "message": result_json["errorMessage"]
                }
            else:
                return {
                    "status": False,
                    "message": "Something went wrong please try,again later"
                }

    def get_client_secret(self):
        data = self.check_connection()
        status = False
        if data['status']:
            url = f"{settings.KEYCLOAK_URL}realms/{settings.KEYCLOAK_REALM}/clients/{settings.KEYCLOAK_CLIENT_ID}/client-secret"
            headers = {
                'Authorization': f'Bearer {data["access_token"]}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            # payload = {
            #         "client_id":clientid,
            #         "username":username,
            #         "password":password,
            #         "grant_type": grant_type,
            #         "client_secret": settings.KEYCLOAK_CLIENT_SECRET
            #         }

            result = requests.get(url, headers=headers)
            print(result, '----------')
            if result.status_code == 200:
                data = result.json()
                print(data, '-------------------------------Data')
                return {"success": True,
                        "data": data
                        }
            else:
                return {
                    "success": False,
                    "message": "User login credentials are wrong please try again"
                }

    def create_group(self, groupname):
        data = self.check_connection()
        if data['status']:
            url = f"{settings.KEYCLOAK_URL}admin/realms/{settings.KEYCLOAK_REALM}/groups"
            headers = {
                'Authorization': f'Bearer {data["access_token"]}',
                'Content-Type': 'application/json'
            }
            payload = {
                "name": groupname,
                "path": "/"+groupname,
                "subGroups": []
            }
            result = requests.post(url, json=payload, headers=headers)

            if result.status_code >= 200 and result.status_code < 300:
                return {
                    "success": True,
                    "message": "Group created successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Sorry,Group not created"
                }

    def get_groups(self):
        data = self.check_connection()
        if data['status']:
            url = f"{settings.KEYCLOAK_URL}admin/realms/{settings.KEYCLOAK_REALM}/groups"
            headers = {
                'Authorization': f'Bearer {data["access_token"]}',
                'Content-Type': 'application/json'
            }
            result = requests.get(url, headers=headers)
            if result.status_code >= 200 and result.status_code < 300:
                data = result.json()
                return {
                    "data": data,
                    "success": True,
                    "message": f"{len(data)} groups found"
                }
            else:
                return {
                    "success": False,
                    "message": "Sorry,Groups not found"
                }

    def login_user(self, clientid, username, password, grant_type):
        url = f"{settings.KEYCLOAK_URL}realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            "username": username,
            "password": password,
            "client_id": clientid,
            "grant_type": grant_type
        }

        result = requests.post(url, data=payload, headers=headers)
        if result.status_code == 200:
            data = result.json()
            return {"success": True,
                    "data": data
                    }
        else:
            return {
                "success": False,
                "message": "User login credentials are wrong please try again"
            }

    def delete_user(self, request):
        pass

# class IsCustomAdminPermission(permissions.BasePermission):
#     def has_permission(self, request, view):
#         userRole=UserRole.objects.get(user=request.user)
#         if userRole.role == "Admin" or userRole.role=="Manager":
#             return True
#         raise CustomForbidden()

# class IsUserKeycloakPermission(permissions.BasePermission, KeyCloakConnection):
#     """Keycloak Check User have permission or not"""
#     def has_permission(self, request, view):
#         data=self.check_user(request)
#         if data:
#             return True
#         raise CustomForbidden()

# class CustomAdminShowTablePermission(permissions.BasePermission):

#     def has_permission(self, request, view):
#         status=True
#         try:
#             id=int(request.data['id'])
#             data=user_list_using_role(request.user)
#             if data['status']:
#                 if not id in data['all_users']:
#                     CustomForbidden()

        # profile=Profile.objects.get(user=request.user)
        # allProfile=Profile.objects.filter(tenant_id=profile.tenant_id)
        # usersList=[value.user_id for value in allProfile]
        # if not id in usersList:
        #     raise CustomForbidden()
        # return status

        # except KeyError:
        #     pass
        # return status
