from django.core.serializers import json
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
# Create your views here.
from store import permissions
from store.filters import ProductFilter, CollectionFilter
from store.models import Product, Collection, Review, Cart, CartItem, Customer, Order, ProductImage, OrderItem, Like
from store.pagination import DefaultPagination
from store.permissions import IsAdminReadOnly, CustomerHistoryPermission, FullDjangoModelPermission

from rest_framework.permissions import IsAuthenticated

# from . import permissions
from store.serializer import ProductSerializer, CollectionSerializer, ReviewSerializer, CartSerializer, \
    AddCartItemSerializer, CartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, OrderSerializer, \
    AddOrderSerializer, UpdateOrderSerializer, ProductImageSerializer, LikeSerializer


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description', 'collection__title']
    ordering_fields = ['unit_price', 'last_update']
    pagination_class = DefaultPagination
    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = Product.objects.annotate(likes_count=Count('likes')).all()
        collection_id = self.request.query_params.get('collection_id')
        if collection_id is not None:
            queryset = queryset.filter(collection_id=collection_id)
        return queryset

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=self.kwargs['pk']):
            return Response({'error': 'product can not be deleted'})
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('product')).all()
    permission_classes = [IsAdminReadOnly]
    serializer_class = CollectionSerializer
    filter_backends = [SearchFilter]
    pagination_class = DefaultPagination
    search_fields = ['title']

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=self.kwargs['pk']):
            return Response({'error': 'Collection can not be deleted'})
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    pagination_class = DefaultPagination

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    serializer_class = ReviewSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}


class CustomerViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        (customer, created) = Customer.objects.get_or_create(user_id=self.request.user.id)
        if self.request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif self.request.method == 'PUT':
            serializer = CustomerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'option', 'head']
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = AddOrderSerializer(data=request.data, context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddOrderSerializer
        if self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        (customer_id, created) = Customer.objects.only('id').get_or_create(user_id=self.request.user.id)
        return Order.objects.filter(customer_id=customer_id)


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer



    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class LikeViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
