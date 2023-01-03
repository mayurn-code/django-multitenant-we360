from django.contrib.auth.models import User
from django.db.utils import DatabaseError
from django.views.generic import FormView
from customers.models import Client, SignUp
from random import choice
from django.conf import settings

# rest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer
from .task import create_new_tenant,send_mail_celery
from django.db.models import Q
import jwt
from .custom_permission import KeyCloakConnection
import uuid
from urllib.parse import urlparse


class SignupView(APIView):
    def post(self, request, *args, **kwargs):
        """
        First time we are storing user details in sign up table
        """
        try:
            firstname = request.data.get('firstname', None)
            lastname = request.data.get('lastname', None)
            company_name = request.data.get('company_name', None)
            email = request.data.get('email', None)
            username = request.data.get('email', '')
            address = request.data.get('address', '')
            city = request.data.get('city', '')
            state = request.data.get('state', '')
            country = request.data.get('country', '')
            zipcode = request.data.get('zipcode', '')
            password = request.data.get("password", None)

            if not company_name:
                return Response({"status": 400,
                                "success": False,
                                 "messages": "Please enter company name"},
                                status=status.HTTP_400_BAD_REQUEST)

            elif len(company_name.split(" ")) < 2:
                return Response({"status": 400,
                                "success": False,
                                 "messages": "Please enter two or more character in company name"},
                                status=status.HTTP_400_BAD_REQUEST)
            elif not email:
                return Response({"status": 400,
                                "success": False,
                                 "messages": "Please enter company email "},
                                status=status.HTTP_400_BAD_REQUEST)
            elif not firstname:
                return Response({"status": 400,
                                "success": False,
                                 "messages": "Please enter firstname "},
                                status=status.HTTP_400_BAD_REQUEST)
            elif not lastname:
                return Response({"status": 400,
                                "success": False,
                                 "messages": "Please enter lastname "},
                                status=status.HTTP_400_BAD_REQUEST)
            elif not password:
                return Response({"status": 400,
                                "success": False,
                                 "messages": "Please enter password "},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                check_email_arr = SignUp.objects.filter(
                    Q(email=email) | Q(username=email))
                if len(check_email_arr) > 0:
                    return Response({
                                    "success": False,
                                    "status": 400,
                                    "messages": "With this email user already exist"},
                                    status=status.HTTP_400_BAD_REQUEST)

                data = {
                    "firstname": firstname.strip(),
                    "lastname": lastname.strip(),
                    "company_name": company_name.strip(),
                    "email": email.strip(),
                    "username": username.strip(),
                    "address": address.strip(),
                    "city": city.strip(),
                    "state": state.strip(),
                    "country": country.strip(),
                    "zipcode": zipcode.strip(),
                    "password": password
                }

                
                """creating a account inside keycloak"""

                usercreate = KeyCloakConnection().create_user(
                    data["username"], data["email"], data["firstname"], data['lastname'], data['password'])

                if usercreate["status"]:
                    user_data = usercreate["data"]

                    """Save data Inside Sign up Table After create account in keycloak"""
                    serializer = SignupSerializer(data=data)

                    if serializer.is_valid():

                        data_user = serializer.save()
                        signup_id = data_user.pk
                        
                        encode_data = {
                            "id": user_data['id'],
                            "email": user_data['email'],
                            "user_id_schma":signup_id
                        }

                        """ Send mail celery """
                        encoded_token = jwt.encode(
                            {'data': encode_data}, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM_CODE)
                        send_mail_celery.delay(email, encoded_token)
                    
                        return Response({"status": 201, "success": True, "data": serializer.data,
                                    "message": "You will get a mail soon please verify your mail, after that you can set up your account "},
                                    status=status.HTTP_201_CREATED)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response({"success": False, "status": 400, "message": usercreate["message"]}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(str(e))
            return Response({"success": False, "status": 500,
                            "message": "Internal server error,please try again later"},
                            status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifySetUpAccount(APIView):
    def get(self, request, token):
        try:
            if not token:
                return Response({"success": False, "status": 400, "message": "Token required"},
                                status.HTTP_400_BAD_REQUEST)
            else:
                decoded_data = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[
                                          settings.JWT_ALGORITHM_CODE])

                if decoded_data:
                    data = decoded_data['data']
                    user_email = data['email']
                    user_id = data['id']
                    user_id_schema = data['user_id_schma']

                    try:
                        """Update User details"""

                        keyCloakClassUpdateEmailVerified = KeyCloakConnection(
                        ).update_user_email_verify_details(user_id)
                        if keyCloakClassUpdateEmailVerified['success']:
                            signupuser = SignUp.objects.get(id=user_id_schema)

                            """Check if Account is already verified"""
                            if signupuser.is_email_verified:
                                return Response({"success": False, "status": 409, "message": "Your account is already verified"},
                                                status.HTTP_409_CONFLICT)
                            else:
                                print("signupuser",signupuser)
                                signupuser.is_email_verified = True
                                signupuser.save()
                                signupuserid = signupuser.pk
                                email = signupuser.email
                                company_name = signupuser.company_name

                                company_name_arr = company_name.split(" ")
                                subdomain = ""

                                if len(company_name_arr) >= 2:
                                    subdomain = company_name_arr[0].lower()

                                clientCheck = Client.objects.filter(
                                    subdomain=subdomain)
                                random_num = uuid.uuid4().hex[:8]
                                if len(clientCheck) >= 1:
                                    subdomain = company_name_arr[0].lower(
                                    )+"_"+str(random_num)

                                """ Create client schema """
                                schema_data = {
                                    'name': company_name,
                                    'domain_url': subdomain+".we360.ai",
                                    'schema_name': subdomain,
                                    'subdomain': subdomain,
                                    "clientid": subdomain,
                                    "basedomain": subdomain+".we360.ai",
                                    "signupuserid": signupuserid
                                }

                                create_new_tenant.delay(schema_data)

                                create_client_res = KeyCloakConnection().create_client(subdomain, company_name)

                                if create_client_res["status"]:
                                    print(create_client_res["message"])
                                else:
                                    return Response({"success": False, "status": 400, "message": create_client_res["message"]},
                                                    status.HTTP_400_BAD_REQUEST)
                                return Response({"success": True, "status": 200, "message": "Account verify successfully"},
                                                status.HTTP_200_OK)
                    except Exception as e:
                        print(str(e))
                        return Response({"success": False, "status": 400, "message": "email not found"},
                                        status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "status": 401, "message": e}, status.HTTP_401_UNAUTHORIZED)


class DomainVerifyingView(APIView):
    def get(self, request):
        try:
            subdomain = request.GET.get('subdomain', None)

            if not subdomain:
                return Response({"success": False, "status": 400, "message": "Subdomain is required"},
                                status.HTTP_400_BAD_REQUEST)
            else:
                clients = Client.objects.filter(
                    subdomain=subdomain.strip().lower())

                if len(clients) >= 1:
                    return Response({"success": False, "status": 400, "message": "Subdomain name already exist"},
                                    status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"success": True, "status": 200, "message": "This subdomain name can use"},
                                    status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "status": 500, "message": e}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        """ User Check"""
        try:
            clientid = request.data.get('clientid', None)
            username = request.data.get('username', None)
            password = request.data.get('password', None)
            grant_type = "password"

            address = request._current_scheme_host + request.path

            url = urlparse(address)

            subdomain = url.hostname.split('.')[0]

            clientsdata = Client.objects.filter(subdomain="zenstack")

            if len(clientsdata) == 0:
                return Response({"status": 400,
                                 "success": False,
                                 "messages": "This subdomain is not valid"},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                if not clientid:
                    return Response({"status": 400,
                                    "success": False,
                                     "messages": "Please enter client id"},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif not username:
                    return Response({"status": 400,
                                    "success": False,
                                     "messages": "Please enter username"},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif not password:
                    return Response({"status": 400,
                                    "success": False,
                                     "messages": "Please enter password"},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif subdomain.lower() != clientid.lower():
                    return Response({"status": 400,
                                    "success": False,
                                     "messages": "Please enter correct client id or subdomain"},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    usercreate = KeyCloakConnection().login_user(
                        clientid, username, password, grant_type)
                    if usercreate["success"]:
                        return Response({"status": 200,
                                        "data": usercreate["data"],
                                         "success": True,
                                         "messages": "Login Success"},
                                        status=status.HTTP_200_OK)
                    else:
                        return Response({"status": 400,
                                        "success": False,
                                         "messages": usercreate["message"]},
                                        status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({"status": 500,
                            "success": False,
                             "messages": "Something went wrong please try again, later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        aa = KeyCloakConnection().get_client_secret()
        print(aa)
        return Response({"data": aa}, status=status.HTTP_200_OK)


class KeycloakGroupView(APIView):
    # create_group
    def post(self, request, *args, **kwargs):
        """Create Group"""
        try:
            groupname = request.data.get('groupname', None)

            if not groupname:
                return Response({"status": 400,
                                "success": False,
                                 "messages": "Please enter groupname"},
                                status=status.HTTP_400_BAD_REQUEST)

            else:
                groupcreate = KeyCloakConnection().create_group(groupname)
                if groupcreate["success"]:
                    return Response({"status": 200,
                                    "success": True,
                                     "messages": groupcreate["message"]},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({"status": 400,
                                    "success": False,
                                     "messages": groupcreate["message"]},
                                    status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({"status": 500,
                            "success": False,
                             "messages": "Something went wrong please try again, later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, req):
        try:
            groupslist = KeyCloakConnection().get_groups()
            return Response(groupslist, status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"status": 500, "message": "Something went wrong,please try again"})


class TenantView(FormView):
    # form_class = GenerateUsersForm
    template_name = "index_tenant.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super(TenantView, self).get_context_data(**kwargs)
        context['tenants_list'] = Client.objects.all()
        context['users'] = User.objects.all()
        return context

    def form_valid(self, form):
        User.objects.all().delete()  # clean current users

        # generate five random users
        USERS_TO_GENERATE = 5
        firstnames = ["Aiden", "Jackson", "Ethan", "Liam", "Mason", "Noah",
                      "Lucas", "Jacob", "Jayden", "Jack", "Sophia", "Emma",
                      "Olivia", "Isabella", "Ava", "Lily", "Zoe", "Chloe",
                      "Mia", "Madison"]
        lastnames = ["Smith", "Brown", "Lee	", "Wilson", "Martin", "Patel",
                     "Taylor", "Wong", "Campbell", "Williams"]

        while User.objects.count() != USERS_TO_GENERATE:
            firstname = choice(firstnames)
            lastname = choice(lastnames)
            try:
                user = User(username=(firstname + lastname).lower(),
                            email="%s@%s.com" % (firstname, lastname),
                            firstname=firstname,
                            lastname=lastname)
                user.save()
            except DatabaseError:
                pass
        return super(TenantView, self).form_valid(form)