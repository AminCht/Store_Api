from django.shortcuts import render
from rest_framework.views import APIView

from store.models import Product, Cart, CartItem
from store.models import Customer
from store.models import Collection
from store.models import Order
from store.models import OrderItem
from django.db.models import Q, F, Value, Func, ExpressionWrapper, DecimalField
from django.db.models.aggregates import Count, Max, Min, Sum, Avg
# Create your views here.
from django.http import HttpResponse
from django.core.mail import send_mail, mail_admins
from django.db import transaction
from django.conf import settings
import requests
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from store.models import Customer
import logging, requests

logger = logging.getLogger(__name__)
class HelloView(APIView):

    def get(self, request):
        try:
            logger.info('calling httpbin')
            response = requests.get('https://httpbin.org/delay/2')
            data = response.json()
            logger.info('recieved a response')
        except requests.ConnectionError:
            logger.critical('htttpbin is offline')
        customer = Customer.objects.filter(id__lt=10).only()
        return render(request, 'hello.html', {'name': list(customer)})


