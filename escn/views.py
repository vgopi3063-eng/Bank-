from django.shortcuts import render,redirect
from .forms import RegisterationForm
from .models import Account
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .utils.send_otp import otp
# Create your views here.
def index(request):
    return render(request,'index.html')

def register(request):
    form=RegisterationForm()
    if request.method =='POST':
        form=RegisterationForm(request.POST,request.FILES)
        if form.is_valid():
            phone=form.cleaned_data['phone']
            form.save()
            data=Account.objects.get(phone=phone)
            send_mail("Thanks for creating Account IN our Bank",f"your Account number is {data.acc_number}\n Thank you \n regrads \n manager \n xxxx",settings.EMAIL_HOST_USER,[data.email],fail_silently=True)
            return redirect('escn')
    context={
        'form':form
    }
    return render(request,'register.html',context)

def pin_gen(request):
    data=None
    if request.method=='POST':
        acc=int(request.POST.get('acc'))
        phone=int(request.POST.get('phone'))
        aadhar=request.POST.get('aadhar')
        try:
            data=Account.objects.get(aadhar=aadhar)
        except:
            messages.error(request,' Aadhar Number is invalid','pin.html')
        if data:
            if data.acc_number==acc:
                if data.phone==phone:
                    one_time_password=otp()
                    request.session['otp']=one_time_password
                    request.session['acc']=data.acc_number
                    send_mail("One Time Password",f"your One Time Password is {one_time_password}\n please don't share with anyone \n Thank you ",settings.EMAIL_HOST_USER,[data.email],fail_silently=True)
                    return redirect('validate')
                else:
                    messages.error(request,'please enter the registered phone number','pin.html')
            else:
                messages.error(request,'please check your account number','pin.html')
    return render(request,'pin.html')

def validate(request):
    if request.method=='POST':
        otp=int(request.session.get('otp'))
        acc=int(request.session.get('acc'))
        opt=int(request.POST.get('opt'))
        pin=int(request.POST.get('pin'))
        c_pin=int(request.POST.get('c_pin'))
        # print(otp,acc,opt,pin,c_pin)
        if otp==opt:
            if pin==c_pin:
                data=Account.objects.get(acc_number=acc)
                data.set_pin(str(pin))
                data.save()
                return redirect('escn')
            else:
                messages.error(request,'PIN Missmatch','validate.html')
        else:
            messages.error(request,'OTP missmatch','validate.html')
    return render(request,'validate.html')

def check_balance(request):
    data = None
    if request.method == "POST":
        acc = request.POST.get('acc')
        pin = request.POST.get('pin')
        # print(acc,pin)
        try:
            data = Account.objects.get(acc_number = acc)
        except:
            messages.error(request,"Account number is Incocrrect")
        if data:
            if int(data.get_pin()) == int(pin):
                # send_mail("Balance Enquiry",f"Your Current Available Balance is {data.balance}\n Thank you  \n xxxx",settings.EMAIL_HOST_USER,[data.email],fail_silently=True)
                messages.error(request,f"Your Current Available Balance is {data.balance}")
                # return redirect('escn')
            else:
                messages.error(request,'invalid pin')
    return render(request,'check_balance.html')

def deposit(request):
    data = None
    if request.method == "POST":
        acc = request.POST.get('acc')
        pin = request.POST.get('pin')
        amt = int(request.POST.get('amt'))
        try:
            data = Account.objects.get(acc_number = acc)
        except :
            messages.error(request,"acc number don't exist ")
        if data:
            if int(data.get_pin()) == int(pin):
                if amt>=100:
                    if amt<=10000:
                        bal = data.balance
                        data.balance = bal+amt
                        data.save()
                        send_mail("AMOUNT CREDITED",f"amount {amt} has been credited to ur account {data.acc_number} via ATM  ur current available balance is {data.balance}",settings.EMAIL_HOST_USER,[data.email],fail_silently=True)
                        return redirect("escn")
                    else:
                        messages.error(request,"please vist the branch for huge amount depsoit")
                else:
                    messages.error(request,"amount is too low for deposit")
            else:
                messages.error(request,'incorrect pin')
    return render(request,"transaction.html")


def withdraw(request):
    data = None
    if request.method == "POST":
        acc = request.POST.get('acc')
        pin = request.POST.get('pin')
        amt = int(request.POST.get('amt'))
        try:
            data = Account.objects.get(acc_number = acc)
        except :
            messages.error(request,"acc number don't exist ")
        if data:
            if int(data.get_pin()) == int(pin):
                if amt>=100:
                    bal = data.balance
                    if amt<=bal:
                        data.balance = bal-amt
                        data.save()
                        send_mail("AMOUNT DEBITED",f"amount {amt} has been debited from ur account {data.acc_number} via ATM  ur current available balance is {data.balance}",settings.EMAIL_HOST_USER,[data.email],fail_silently=True)
                        return redirect("escn")
                    else:
                        messages.error(request,"insuffucent funds")
                else:
                    messages.error(request,"bichagaduu")
            else:
                messages.error(request,'incorrect pin')
    context = {
        'flag':True
    }
    return render(request,"transaction.html",context)

def acc_transfer(request):
    f_data = None
    t_data = None
    if request.method == "POST":
        f_acc = request.POST.get('f_acc')
        t_acc = request.POST.get('t_acc')
        pin = request.POST.get('pin')
        amt = int(request.POST.get('amt'))
        try:
            f_data = Account.objects.get(acc_number = f_acc)
        except :
            messages.error(request,"sender account number is invlaid")
        try:
            t_data = Account.objects.get(acc_number = t_acc)
        except:
            messages.error(request,"Receiver Account is invalid")
        if f_data:
            if int(f_data.get_pin())== int(pin):
                bal = f_data.balance
                if amt>=1:
                    if amt<=bal:
                        f_data.balance = bal-amt
                        f_data.save()
                        send_mail("AMOUNT DEBITED",f"amount {amt} has been debited from ur account {f_data.acc_number} via Account transfer  ur current available balance is {f_data.balance}",settings.EMAIL_HOST_USER,[f_data.email],fail_silently=True)
                        if t_data:
                            t_data.balance = amt+t_data.balance
                            t_data.save()
                            send_mail("AMOUNT CREDITED",f"amount {amt} has been credited to ur account {t_data.acc_number} via ATM  ur current available balance is {t_data.balance}",settings.EMAIL_HOST_USER,[t_data.email],fail_silently=True)
                            return redirect("escn")
                else:
                    messages.error(request,"kanisam 1 rs leka potey why ...")
    return render(request,'acc_tran.html')
