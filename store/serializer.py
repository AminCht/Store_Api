from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from store.models import Product, Collection, Review, Cart, CartItem, Customer, Order, OrderItem, ProductImage, Like


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    def create(self, validated_data):
        ProductImage.objects.create(product_id=self.context['product_id'], **validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'collection', 'likes_count', 'images']

    likes_count = serializers.IntegerField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'description', 'date', 'product']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, item: CartItem):
        return item.quantity * item.product.unit_price
    product = ProductSerializer()


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

    items = CartItemSerializer(many=True, read_only=True)
    id = serializers.UUIDField(read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        return sum(item.product.unit_price * item.quantity for item in cart.items.all())


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if Product.objects.filter(pk=value).count() == 0:
            raise serializers.ValidationError('no product found')
        return value

    def save(self, **kwargs):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']
        try:
            cart_item = CartItem.objects.get(product_id=product_id, cart_id=cart_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']

    user_id = serializers.IntegerField(read_only=True)


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'payment_status', 'items', 'placed_at', 'customer']


class AddOrderSerializer(serializers.ModelSerializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, value):
        if not Cart.objects.filter(pk=value).exists():
            raise serializers.ValidationError('There is not any cart with this given id')
        if CartItem.objects.filter(cart_id=value).count() == 0:
            raise serializers.ValidationError('cart is Empty')
        return value

    class Meta:
        model = Order
        fields = ['cart_id']

    def save(self, **kwargs):

        cart_id = self.validated_data['cart_id']
        user_id = self.context['user_id']
        with transaction.atomic():
            (customer, create) = Customer.objects.get_or_create(user_id=user_id)
            order = Order.objects.create(customer=customer)
            cart_items = CartItem.objects.filter(cart_id=cart_id)
            order_items = [OrderItem(
                order=order,
                product=items.product,
                unit_price=items.product.unit_price,
                quantity=items.quantity
                )for items in cart_items]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=cart_id).delete()
            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['payment_status']


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'product_id']
    product_id = serializers.IntegerField()
