from django.contrib import admin
from django.urls import path, include
from mainapp.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account', account, name='account'),
    path('logoutuser', logoutuser, name='logoutuser'),
    path('', homepage, name='homepage'),
    path('showproduct', showproduct, name='showproduct'),
    path('signup', signup, name='signup'),
    path('login', loginview, name='login'),
    path('addtocart', addtocart, name='addtocart'),
    path('cart', cart, name='cart'),
    path('deleteitem', deleteitem, name='deleteitem'),
    path('history', history, name='history'),
    path('submitorder', submitorder, name='submitorder'),
    path('getphonenumber', getphonenumber, name='getphonenumber'),
    path('getpassword', getpassword, name='getpassword'),
    path('getotp', getotp, name='getotp'),
    path('removefilter', homepage, name='removefilter'),
    path('handlesearch', handlesearch, name='handlesearch'),
    path('autocomplete/', ProductAutocomplete.as_view(), name='product-autocomplete'),
    path('testing', TemplateView.as_view(template_name="temptemp.html"), name='testing'),
    path('paymentsuccess', paymentsuccess, name='paymentsuccess'),
    path('/accounts/login/?next=/cart', cart, name='accounts/login/?next=/cart'),
    path('products', products, name='products')
    ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
