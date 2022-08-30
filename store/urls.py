from django.conf.urls.static import static
from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from django.conf import settings

from .views import ProductImageViewSet

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='product')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')
router.register('likes', views.LikeViewSet, basename='likes')
product_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
product_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
product_router.register('images', ProductImageViewSet, basename='product-images')
cart_items_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_items_router.register('items', views.CartItemViewSet, basename='cart-items')
urlpatterns = router.urls + product_router.urls + cart_items_router.urls

