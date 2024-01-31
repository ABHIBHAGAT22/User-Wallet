from django.contrib import admin
from .models import balance, otpauth, userapp, transcations



class UserAdmin(admin.ModelAdmin):
    list_display =['user_id','username','emailId','created_At']

admin.site.register(userapp,UserAdmin)


class otpAdmin(admin.ModelAdmin):
    list_display =['user_id','signup_otp','created_At','signin_otp','login_at','verified_status']

admin.site.register(otpauth,otpAdmin)


# Register your models here.
class TranscationAdmin(admin.ModelAdmin):
    list_display =['id','user_id','sender_emailId','receiver_emailId','transcation_status','Amount','payment_at']
    class Meta:
      app_label = 'Transcation'

admin.site.register(transcations,TranscationAdmin)

class BalanceAdmin(admin.ModelAdmin):
    list_display =['user_id','balance','last_updated_at']
    class Meta:
      app_label = 'Balance'

admin.site.register(balance,BalanceAdmin)


