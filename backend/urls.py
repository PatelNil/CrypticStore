from django.contrib import admin
from django.contrib.auth import logout
from django.urls import path, include
from backend import views
from django.conf import settings
from django.conf.urls.static import  static
# from rest_framework.urlpatterns import format_suffix_patterns

app_name='backend'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.signin,name='signin'),
    path(r'^postin/',views.postin,name='postin'),
    path(r'^logout/',views.log_out,name='logout'),
    path(r'^signup/',views.signUp,name='signup'),
    path(r'^postsignup/',views.postsignup,name='postsignup'),
    path(r'^/create/',views.create,name='create'),
    path(r'^postreport/',views.postreport,name='postreport'),
    path(r'^/check/',views.check,name='check'),
    path(r'^/decrypt/',views.decrypt,name='decrypt'),
    path(r'^/aboutus/',views.aboutus,name='aboutus'),
    path(r'^to_decrypt/',views.to_decrypt,name='to_decrypt'),
    path('post_check/',views.post_check,name='post_check'),
    path('fileUpload/',views.fileUpload,name='fileUpload'),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
 
# urlpatterns = format_suffix_patterns(urlpatterns)
