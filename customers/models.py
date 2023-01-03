from django.db import models

# Create your models here.
from django.db import models
from tenant_schemas.models import TenantMixin

class SignUp(models.Model):
    email = models.EmailField(max_length=300,unique=True)
    username = models.CharField(max_length=300,unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    company_name = models.CharField(max_length=300)
    address = models.CharField(max_length=200,default=None)
    city = models.CharField(max_length=200,default=None)
    state = models.CharField(max_length=200,default=None)
    country = models.CharField(max_length=200,default=None)
    zipcode = models.CharField(max_length=10,default=None)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.company_name




class Client(TenantMixin):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200)
    created_on = models.DateField(auto_now_add=True)
    subdomain = models.CharField(max_length=300,default=None,null=True,blank=True)
    basedomain = models.CharField(max_length=300,default=None,null=True,blank=True)
    clientid = models.CharField(max_length=300,default=None,null=True,blank=True)
    signupuserid = models.ForeignKey(SignUp,null=True,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name



# tenant = Client(domain_url='tenant5.my-domain.com', # don't add your port or www here!
#                 schema_name='tenant5',
#                 name='Mayur Tenant5')
# tenant.save()