from django.core.checks.messages import Error
from django.http.response import HttpResponse
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages
from wallet_management.models import *
from django.core.mail import EmailMessage
from django.db.models import Q
import math
import random
from datetime import datetime, timedelta

# # ------------------------------------WELCOME PAGE ------------------------------------------------------#
def index(request):
    messages.success(request,"Welcome to the User Wallet!")
    return render(request,'index.html')

#------------------------------------DASHBOARD PAGE -----------------------------------------------------#
def dash(request):
        request.session.modified = True
        if request.session.get('loggedin',False)==False:
            messages.success(request,"You need to sign in first!")
            return redirect('/login')
        # messages.success(request,"Welcome to dashboard!")
        user_id=request.session['user_id']
        user_obj=userapp.objects.get(user_id=user_id)
        balance_obj=balance.objects.get(user_id=user_obj)  
        context = {'name' : user_obj.username,'balance':balance_obj.balance}
        return render(request,'home.html',context)

#--------------------------------SIGN-UP PAGE------------------------------------------------------------#
def signup(request):
    # print(request.method)
    if request.method == "POST":
        username=request.POST.get('username')
        emailId=request.POST.get('emailId')
        
         # print(username,emailId)

        check_user=userapp.objects.filter(emailId=emailId)
        if check_user:
            messages.success(request,"User Already Exist")
            return render(request,'register.html')
       
        user_obj=userapp.objects.create(emailId=emailId,username=username)
        balance.objects.create(user_id=user_obj,balance=0)
        request.session['user_id']=user_obj.user_id
        
        subject='Verify your email'
        digits = "0123456789"
        signup_otp = ""
        for i in range(4):
            signup_otp += str(digits[math.floor(random.random() * 10)])    
        message='Your OTP for email verification is '+signup_otp
       
        from_email= settings.EMAIL_HOST_USER
       
        to_list = [emailId]
      
        email = EmailMessage(subject,message,from_email,to_list)
        email.fail_silently = False
        email.send()
        messages.success(request,"OTP sent on your Email!")
        otpauth.objects.create(user_id=user_obj,signup_otp=signup_otp)
       
        return redirect('/otpverify1')
    return render(request,'register.html')

def is_otp_expired(timestamp, timeout_minutes=5):
    # print(type(timestamp))  # <class 'datetime.datetime'>
    
    # Convert timestamp to float
    timestamp_float = timestamp.timestamp()

    current_time = datetime.now().timestamp()
    # print(current_time)  

    elapsed_time = current_time - timestamp_float
    # print(elapsed_time)
    return elapsed_time > (timeout_minutes * 60)
#------------------------- OTP VERIFICATION AFTER SIGN-UP PAGE--------------------------------------------------#   
def otpverify1(request):
    user_id=request.session['user_id']
    if request.method == 'POST':
        signup_otp = request.POST.get('otp')
        otp_obj = otpauth.objects.get(user_id=user_id)
        if signup_otp == otp_obj.signup_otp:

            otp_obj.verified_status=True
            otp_obj.save()
            messages.success(request,"Successfully Registered!")
            return redirect('/login')
        else:
            messages.success(request,"Invalid OTP,Try Again!")
            return redirect('/otpverify1')
    
    return render(request,'otp_for_signup.html')
    

#------------------------------------SIGN-IN PAGE--------------------------------------------------------------#
def signin(request):
  
    if request.method == "POST":
        emailId=request.POST.get('emailId')
        user_obj=userapp.objects.filter(emailId=emailId).first()

        if user_obj is not None:
            otp_obj=otpauth.objects.get(user_id=user_obj)       
            if otp_obj.verified_status==True: 
                subject='UserWallet - Sign In OTP Verification'
                digits = "0123456789"
                signin_otp = ""
                for i in range(4) :
                    signin_otp += str(digits[math.floor(random.random() * 10)])   
                message = (f"Hi {user_obj.username},\n"
                           f"Thank you for signing in to UserWallet. To ensure the security of your account," 
                           f"please use the following OTP for verification: {signin_otp}."
                           f"This OTP is valid for a single use and will expire shortly.\n"
                           f"Thank you,\n"
                           f"UserWallet Team\n")  
        
                from_email= settings.EMAIL_HOST_USER
                to_list = [emailId]
                email = EmailMessage(subject,message,from_email,to_list)
                email.fail_silently = False
                email.send()
                messages.success(request,"OTP sent on your Email!")
                otp_obj.signin_otp = signin_otp
                otp_obj.save()
                request.session['user_id']=user_obj.user_id
                request.session['emailId']=emailId
               
                return redirect('/otpverify2')
            request.session['user_id']=user_obj.user_id

            messages.success(request,"Verify your Account!")
            return redirect('/otpverify1')
        else:
            messages.success(request,"User Not Found")
            return render(request,'login.html')
           
    return render(request,'login.html')

#---------------------------------------OTP VERIFICATION AFTER SIGN IN PAGE-------------------------------------------#    
def otpverify2(request):
    user_id=request.session['user_id']
    otp_obj=otpauth.objects.get(user_id=user_id)       
    if request.method == 'POST':
    
        enter_otp = request.POST.get('otp')
      
        otp_obj = otpauth.objects.filter(user_id=user_id).first()     
        
        if enter_otp == otp_obj.signin_otp:
            
            if is_otp_expired(otp_obj.created_At, timeout_minutes=5):
                messages.success(request,"OTP has expired, generate new OTP again !")
                return redirect('/login')
            else:
                messages.success(request,"Successfully login")
                request.session['user_id']=user_id
                request.session['loggedin']=True

                balance_obj=balance.objects.get(user_id=user_id)      
                request.session['Amount']=balance_obj.balance
                return redirect('/dash')
        else:
            messages.success(request,"Invalid OTP, Try again!")

        return redirect('/otpverify2')
    return render(request,'otp_for_signin.html' )
    

#---------------------------------------------ADD MONEY PAGE------------------------------------------------------------------------#
def addmoney(request):
        if request.session.get('loggedin',False)==False:
            messages.success(request,"You need to sign in first!")
            return redirect('/signin')
        #-----------for displying name and balance on add money page-----------------#
        emailId = request.session['emailId']
        user_id=request.session['user_id']
        user_obj=userapp.objects.get(user_id=user_id)           
        balance_obj=balance.objects.get(user_id=user_obj)
        context = {'name' : user_obj.username,'balance':balance_obj.balance}
    
        if request.method == "POST":
          
            Amount=request.POST.get('Amount')
            if int(Amount)>0 and int(Amount)<=10000:
                Inital_balance=balance_obj.balance
                Current_Balance=int(Inital_balance)+int(Amount)
                balance_obj.balance=Current_Balance
                balance_obj.save()
                transcations.objects.create(user_id=user_obj,sender_emailId=emailId,receiver_emailId=emailId,transcation_status="1",Amount=Amount)
                messages.success(request,'Successfully added money to your account')
                return redirect('/dash')
            messages.success(request,"Entered Money is Invalid, Try again!")
            return redirect('/addmoney')
        return render(request,'addmoney.html',context=context)
    

#-------------------------------------------------SEND MONEY PAGE------------------------------------------------------------------#
def sendmoney(request):
        if request.session.get('loggedin',False)==False:
            messages.success(request,"You need to sign in first!")
            return redirect('/login')
        emailId = request.session['emailId']
        user_id = request.session['user_id']

        #-----------------login user-------------------------------------------#
        loginuser_obj=userapp.objects.get(user_id=user_id)
        loginbalance_obj=balance.objects.get(user_id=loginuser_obj)
        context = {'name' : loginuser_obj.username,'balance':loginbalance_obj.balance}
    
        if request.method == "POST":
            receiver_emailId=request.POST.get('emailId')
            Amount=request.POST.get('Amount')
            check_user = userapp.objects.filter(emailId = receiver_emailId).first() 
            
            if check_user is None:
                messages.success(request,'User Not Found')
                return redirect('/sendmoney')

            if check_user.emailId!=emailId:
            
                otp_obj=otpauth.objects.get(user_id=check_user.user_id)
                if otp_obj.verified_status==False:
                    messages.success(request,'User Not Verified')    
            
                if loginbalance_obj.balance==0:
                    messages.success(request,'Zero Balance')
                    return redirect('/sendmoney')
                elif loginbalance_obj.balance>=int(Amount):  
                    transcations.objects.create(user_id=loginuser_obj,sender_emailId=loginuser_obj.emailId,receiver_emailId=receiver_emailId,transcation_status="-1",Amount=Amount)
                    current_balance=loginbalance_obj.balance-int(Amount)
                    loginbalance_obj.balance=current_balance 
                    loginbalance_obj.save()
                    transcations.objects.create(user_id=check_user,sender_emailId=receiver_emailId,receiver_emailId=loginuser_obj.emailId,transcation_status="+2",Amount=Amount)
                    Receiver_obj=balance.objects.get(user_id=check_user)
                    current_balance2=Receiver_obj.balance+int(Amount)
                    Receiver_obj.balance=current_balance2
                    Receiver_obj.save()
                    messages.success(request,'Successfully sent money!')
                    return redirect('/dash')
                   
                messages.success(request,'Not Sufficient balance')
            messages.success(request,"You can not send money to youself, Try add money feature")
    
        return render(request,'sendmoney.html',context=context)
    
#------------------------------------TRANSCATION HISTORY---------------------------------------------------------------------------#
def history(request):
        if request.session.get('loggedin',False)==False:
            messages.success(request,"You need to sign in first!")
            return redirect('/login')
       
        emailId = request.session['emailId']
        user_id = request.session['user_id']
        user_obj=userapp.objects.get(user_id=user_id)
        # print(user_obj)
        balance_obj=balance.objects.get(user_id=user_obj)
        t=transcations.objects.filter(Q(sender_emailId=emailId)).all()
        context = {'name' : user_obj.username,'balance':balance_obj.balance,'t':t,'user_id':user_id}
        # print('context:',context)
        # print("t:",t)
        # for i in t:
             # print(i.Amount)
        return render(request,'history.html',context=context)
    

#--------------------------------------LOGOUT--------------------------------------------------------------------------------------#
def logout(request):
    if request.session.get('loggedin',False)==False:
            messages.success(request,"You need to sign in first!")
            return redirect('/login')
    del request.session['loggedin']
    messages.success(request,'Successfully Logout')
    return render(request,'logout.html')

#-------------------------------------------------END-----------------------------------------------------------------------------#
