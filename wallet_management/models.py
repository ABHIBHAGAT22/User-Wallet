from django.db import models
from django.db.models.fields import BigAutoField
# Create your models here.

class userapp(models.Model):
    user_id=BigAutoField(primary_key=True)
    username = models.CharField(max_length=60,null = True,blank = True,default=None)
    emailId=models.EmailField()
    created_At=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user_id) 

class otpauth(models.Model):
    user_id=models.ForeignKey(userapp,on_delete=models.CASCADE,null=False,to_field='user_id')
    signup_otp = models.CharField(max_length=4,null=False)
    signin_otp = models.CharField(max_length=4,null=False)
    login_at = models.DateTimeField(auto_now=True)
    created_At = models.DateTimeField(auto_now=True)
    verified_status=models.BooleanField(null = True,blank = True,default=False)
    
    def __str__(self):
            return str(self.user_id) 

class transcations(models.Model):
    user_id=models.ForeignKey(userapp,on_delete=models.CASCADE,default=None,to_field='user_id',null = True,blank = True)
    sender_emailId=models.EmailField()
    receiver_emailId=models.EmailField()
    transcation_status=models.CharField(max_length=2)
    Amount=models.BigIntegerField(default=None, editable=False)
    payment_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return str(self.user_id)

class balance(models.Model):
    user_id=models.ForeignKey(userapp,on_delete=models.CASCADE,default=None,to_field='user_id',null = False)
    balance=models.BigIntegerField(default=None, editable=False)
    last_updated_at=models.DateTimeField(auto_now=True)


    def __str__(self):
            return str(self.user_id)
        
