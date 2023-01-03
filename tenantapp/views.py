# rest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from datetime import datetime

# db connection
from django.db import connection


# Create your views here.

class HotelView(APIView):

    def post(self,request):
        """
        First time we are storing user details in sign up table
        """
        try:
            hotel_name = request.data.get('name',None)
            authorization = request.META.get("HTTP_AUTHORIZATION",None)
            if authorization==None or authorization=="":
                return Response({"status":400,
                                "success":False,
                                "messages":"Bearer token required"}, 
                                status=status.HTTP_400_BAD_REQUEST)

            elif hotel_name == None or hotel_name == "":
                return Response({"status":400,
                                "success":False,
                                "messages":"Please enter name"}, 
                                status=status.HTTP_400_BAD_REQUEST)

            else:
                removeBearer = authorization.replace('Bearer ','')

                decode_code = jwt.decode(removeBearer,options={"verify_signature": False},algorithms=['RS256'])
                client_id = ''

                if decode_code["azp"]:
                    client_id = decode_code["azp"]
                try:    
                    with connection.cursor() as cursor:
                        query = f"""
                        INSERT INTO {client_id}.tenantapp_hotels 
                        (hotel_name) values('{hotel_name}')
                        """
                        cursor.execute(query)
                        return Response({"success":True,"status":200,
                                "data":{"name":hotel_name},
                                "message":"Hotel created successfully"},
                                status.HTTP_200_OK)
                except Exception as e:
                    print(str(e))
                    return Response({"success":False,"status":400,
                                "message":str(e)},
                                status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({"success":False,"status":500,
                            "message":"Internal server error,please try again later"},
                            status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self,request):
        try:

            authorization = request.META.get("HTTP_AUTHORIZATION")

            if authorization==None or authorization=="":
                return Response({"status":400,
                                "success":False,
                                "messages":"Bearer token required"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                removeBearer = authorization.replace('Bearer ','')

                decode_code = jwt.decode(removeBearer,options={"verify_signature": False},algorithms=['RS256'])
           
                expiration_dateTime = decode_code["exp"]
       
                if datetime.now() >= datetime.fromtimestamp(expiration_dateTime):
                    print("Token Expired")
                    return Response({"status":400,
                                "success":False,
                                "messages":"Token Expired"}, 
                                status=status.HTTP_400_BAD_REQUEST)
                else:
                    client_id = ''
                    if decode_code["azp"]:
                        client_id = decode_code["azp"]
                    try:    
                        with connection.cursor() as cursor:
                            query = f'''Select * from  {str(client_id)}.tenantapp_hotels '''
                            cursor.execute(query)
                            data = cursor.fetchall()
                            tempData = []
                            if data != None or data != []:
                                for item in data:
                                    tempData.append({"id":item[0],"name":item[1]})
                        
                            return Response({"success":True,"status":200,
                                    "data":tempData,
                                    "message":f"{len(tempData)} data found"},
                                    status.HTTP_200_OK)

                    except Exception as e:
                        print(str(e))
                        return Response({"success":False,"status":400,
                                    "message":str(e)},
                                    status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response({"success":False,"status":500,
                            "message":"Internal server error,please try again later"},
                            status.HTTP_500_INTERNAL_SERVER_ERROR)

