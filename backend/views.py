import os
from django.http.response import HttpResponse
from django.shortcuts import render 
import pyrebase
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.views.generic.base import RedirectView
import pyAesCrypt
import mimetypes
config={
  'apiKey': "AIzaSyDkEtETtizrO_fRmVAL13iJDnGrHU7eHrs",
    'authDomain': "cnsproject-61c6b.firebaseapp.com",
    'databaseURL': "https://cnsproject-61c6b-default-rtdb.firebaseio.com",
    'projectId': "cnsproject-61c6b",
    'storageBucket': "cnsproject-61c6b.appspot.com",
    'messagingSenderId': "32455541554",
    'appId': "1:32455541554:web:14c1ce213f650acd780d2b",
    'measurementId': "G-PLKLSY1EPN"
}
firebase=pyrebase.initialize_app(config) 
authe = firebase.auth() 
database = firebase.database()
storage = firebase.storage()
def signin(request):
    return render(request,'signin.html')

def postin(request):
    try:
        email = request.POST['email']
        password = request.POST['pass']
        try:
            user = authe.sign_in_with_email_and_password(email,password)
            request.session['key'] = password
            request.session['uid'] = str(user['idToken'])
            idtoken = request.session['uid']
            a = authe.get_account_info(idtoken)
            a = a['users']
            a = a[0]
            a = a['localId']
            name = database.child('users').child(a).child('details').child('name').get().val()
            request.session['name'] = name
            return render(request,'postin.html',{'email':name})
        except:
            print("Error")
            message='Invaid Credentials'
            return render(request,'signin.html',{'messg':message})
    except:
        name = request.session['name']
        print(request.session['key'])
        return render(request,'postin.html',{'email':name})

def log_out(request):
    logout(request)
    return render(request,'signin.html')

def signUp(request):
    return render(request,"signup.html")

def postsignup(request):
    name=request.POST.get('name')
    email=request.POST.get('email')
    passw=request.POST.get('password')
    try:
        user=authe.create_user_with_email_and_password(email,passw)
        uid = user['localId']
        data={"name":name,"status":"1"}
        database.child("users").child(uid).child("details").set(data)
    except:
        message="Unable to create account try again"
        return render(request,"signup.html",{"messg":message})
    message="User created successfully"
    return render(request,"signin.html",{"messg":message})

def create(request):
    return render(request,"create.html")

def postreport(request):
    title = request.POST['title']
    details = request.POST.get('details')
    #url = request.POST['url']
    data ={
        'title':title,
        'details':details,
        'url':url
    }
    import time
    from datetime import datetime, timezone
    import pytz

    tz= pytz.timezone('Asia/Kolkata')
    time_now= datetime.now(timezone.utc).astimezone(tz)
    time_ = int(time.mktime(time_now.timetuple()))
    idToken = request.session['uid']
    user_ = authe.get_account_info(idToken)
    user_ = user_['users']
    user_ = user_[0]
    user_ = user_['localId']
    database.child('users').child(user_).child('reports').child(time_).set(data)
    name = database.child('users').child(user_).child('details').child('name').get().val()
    print(name)
    return render(request,'postin.html', {'email':name})

def check(request):
    import datetime
    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']

    timestamps = database.child('users').child(a).child('reports').shallow().get().val()#list of timestamps
    if timestamps != None:
        lis_time=[]
        for i in timestamps:
            lis_time.append(i)
        lis_time.sort(reverse=True)
        work = []
        for i in lis_time:
            wor=database.child('users').child(a).child('reports').child(i).child('title').get().val()
            work.append(wor)
        date=[]
        for i in lis_time:
           i = float(i)
           dat = datetime.datetime.fromtimestamp(i).strftime('%H:%M %d-%m-%Y')
           date.append(dat)
        comb_lis = zip(lis_time,date,work)
        name = database.child('users').child(a).child('details').child('name').get().val()
        return render(request,'check.html',{'data':comb_lis})
    else:
        return render(request,'check.html')

def post_check(request):

    import datetime

    time = request.GET.get('z')

    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    print(a)
    work =database.child('users').child(a).child('reports').child(time).child('title').get().val()
    progress =database.child('users').child(a).child('reports').child(time).child('details').get().val()
    url =database.child('users').child(a).child('reports').child(time).child('url').get().val()
    print(work)
    #i =float(time)
    #dat = datetime.datetime.fromtimestamp(i).strftime('%H:%M %d-%m-%Y')
    name = database.child('users').child(a).child('details').child('name').get().val()
    
    return render(request,'post_check.html',{'w':work,'p':progress,'e':name,'u':url})

@csrf_exempt
def fileUpload(request):
    # encryption/decryption buffer size - 64K 
    global url  
    fs = FileSystemStorage()
    bufferSize = 64 * 1024  
    password = request.session['key']
    f1 = request.FILES['uploadedFile']
    saved = fs.save(f1.name,f1)
    name = fs.url(saved)
    n1 = name.split('/')[-1]
    try:
        err = pyAesCrypt.encryptFile("media/"+n1,"media/"+n1+".aes",password, bufferSize)
        print(err)
    except:
        return HttpResponse('not')
    path_on_cloud = 'files/'+n1+".aes"
    path_on_local = "media/"+n1+".aes"
    storage.child(path_on_cloud).put(path_on_local)
    url = storage.child(path_on_cloud).get_url(request.session['uid'])
    os.remove(path_on_local)
    os.remove("media/"+n1)
    return render(request,'create_title.html',{'file_id':name})


def decrypt(request):
    return render(request,'decrypt.html')

def aboutus(request):
    return render(request,'aboutus.html')

def to_decrypt(request):
    # encryption/decryption buffer size - 64K  
    extentions = ['txt','pdf','png','jpg','jpeg','py'] 
    bufferSize = 64 * 1024  
    file1 = request.FILES['file1']
    password = request.session['key']
    fs = FileSystemStorage()
    filename = fs.save(file1.name,file1)
    name = fs.url(filename)
    n1 = name.split('/')[-1]
    ext = ""
    for ex in extentions:
        if n1.find("."+ex)!=-1:
            ext = ex
            decrypt = pyAesCrypt.decryptFile("media/"+n1,"media/"+n1+"."+ex, password, bufferSize )
    fl_path = "media/"+n1+"."+ext
    filename = n1+"."+ext
    fs1 = FileSystemStorage()
    with fs1.open(filename) as data:
        mime_type, _ = mimetypes.guess_type(fl_path)
        response = HttpResponse(data, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
    os.remove("media/"+n1)
    os.remove("media/"+n1+"."+ext)
    return response


