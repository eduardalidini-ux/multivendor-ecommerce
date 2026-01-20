# Django Packages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.db import transaction
from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string


# Restframework Packages
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import status

# Serializers
from userauths.serializer import MyTokenObtainPairSerializer, RegisterSerializer
from store.serializers import CancelledOrderSerializer, CartSerializer, CartOrderItemSerializer, CouponUsersSerializer, ProductSerializer, TagSerializer ,CategorySerializer, DeliveryCouriersSerializer, CartOrderSerializer, GallerySerializer, BrandSerializer, ProductFaqSerializer, ReviewSerializer,  SpecificationSerializer, CouponSerializer, ColorSerializer, SizeSerializer, AddressSerializer, WishlistSerializer, ConfigSettingsSerializer

# Models
from userauths.models import User
from store.models import CancelledOrder, CartOrderItem, CouponUsers, Cart, Notification, Product, Tag ,Category, DeliveryCouriers, CartOrder, Gallery, Brand, ProductFaq, Review,  Specification, Coupon, Color, Size, Address, Wishlist
from addon.models import ConfigSettings, Tax
from vendor.models import Vendor

# Others Packages
import json
from decimal import Decimal
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def send_notification(user=None, vendor=None, order=None, order_item=None):
    Notification.objects.create(
        user=user,
        vendor=vendor,
        order=order,
        order_item=order_item,
    )

class ConfigSettingsDetailView(generics.RetrieveAPIView):
    serializer_class = ConfigSettingsSerializer

    def get_object(self):
        # Use the get method to retrieve the first ConfigSettings object
        return ConfigSettings.objects.first()

    permission_classes = (AllowAny,)

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(active=True)
    permission_classes = (AllowAny,)


class BrandListView(generics.ListAPIView):
    serializer_class = BrandSerializer
    queryset = Brand.objects.filter(active=True)
    permission_classes = (AllowAny,)

class FeaturedProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(status="published", featured=True)[:3]
    permission_classes = (AllowAny,)

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(status="published")
    permission_classes = (AllowAny,)

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer

    def get_object(self):
        # Retrieve the product using the provided slug from the URL
        slug = self.kwargs.get('slug')
        return Product.objects.get(slug=slug)
    
class CartApiView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        payload = request.data

        required_fields = [
            "product",
            "qty",
            "price",
            "shipping_amount",
            "country",
            "size",
            "color",
            "cart_id",
        ]
        missing = [f for f in required_fields if payload.get(f) in (None, "")]
        if missing:
            return Response(
                {"message": "Missing required fields", "missing": missing},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product_id = payload.get("product")
        user_id = payload.get("user")
        qty_raw = payload.get("qty")
        price_raw = payload.get("price")
        shipping_amount_raw = payload.get("shipping_amount")
        country = payload.get("country")
        size = payload.get("size")
        color = payload.get("color")
        cart_id = payload.get("cart_id")

        product = Product.objects.filter(status="published", id=product_id).first()
        if not product:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        user = None
        if user_id not in (None, "", "undefined", "null", 0, "0"):
            user = User.objects.filter(id=user_id).first()

        try:
            qty = int(qty_raw)
            if qty < 1:
                raise ValueError("qty must be >= 1")
        except Exception:
            return Response({"message": "Invalid qty"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            price = Decimal(str(price_raw))
            shipping_amount = Decimal(str(shipping_amount_raw))
        except Exception:
            return Response({"message": "Invalid price/shipping_amount"}, status=status.HTTP_400_BAD_REQUEST)
        
        tax = Tax.objects.filter(country=country).first()
        if tax:
            tax_rate = tax.rate / 100
            
        else:
            tax_rate = 0

        cart = Cart.objects.filter(cart_id=cart_id, product=product).first()

        if cart:
            cart.product = product
            cart.user = user
            cart.qty = qty
            cart.price = price
            cart.sub_total = price * qty
            cart.shipping_amount = shipping_amount * qty
            cart.size = size
            cart.tax_fee = qty * Decimal(tax_rate)
            cart.color = color
            cart.country = country
            cart.cart_id = cart_id

            config_settings = ConfigSettings.objects.first()

            service_fee_charge_type = getattr(config_settings, "service_fee_charge_type", "percentage")
            service_fee_percentage_value = getattr(config_settings, "service_fee_percentage", 0)
            service_fee_flat_rate_value = getattr(config_settings, "service_fee_flat_rate", Decimal("0"))

            if service_fee_charge_type == "percentage":
                service_fee_percentage = Decimal(service_fee_percentage_value) / Decimal("100")
                cart.service_fee = service_fee_percentage * cart.sub_total
            else:
                cart.service_fee = Decimal(service_fee_flat_rate_value)

            cart.total = cart.sub_total + cart.shipping_amount + cart.service_fee + cart.tax_fee
            cart.save()

            return Response({"message": "Cart updated successfully"}, status=status.HTTP_200_OK)
        else:
            cart = Cart()
            cart.product = product
            cart.user = user
            cart.qty = qty
            cart.price = price
            cart.sub_total = price * qty
            cart.shipping_amount = shipping_amount * qty
            cart.size = size
            cart.tax_fee = qty * Decimal(tax_rate)
            cart.color = color
            cart.country = country
            cart.cart_id = cart_id

            config_settings = ConfigSettings.objects.first()

            service_fee_charge_type = getattr(config_settings, "service_fee_charge_type", "percentage")
            service_fee_percentage_value = getattr(config_settings, "service_fee_percentage", 0)
            service_fee_flat_rate_value = getattr(config_settings, "service_fee_flat_rate", Decimal("0"))

            if service_fee_charge_type == "percentage":
                service_fee_percentage = Decimal(service_fee_percentage_value) / Decimal("100")
                cart.service_fee = service_fee_percentage * cart.sub_total
            else:
                cart.service_fee = Decimal(service_fee_flat_rate_value)

            cart.total = cart.sub_total + cart.shipping_amount + cart.service_fee + cart.tax_fee
            cart.save()

            return Response( {"message": "Cart Created Successfully"}, status=status.HTTP_201_CREATED)


class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        user_id = self.kwargs.get('user_id')  # Use get() method to handle the case where user_id is not present

        
        if user_id is not None:
            user = User.objects.get(id=user_id)
            queryset = Cart.objects.filter(Q(user=user, cart_id=cart_id) | Q(user=user))
        else:
            queryset = Cart.objects.filter(cart_id=cart_id)
        
        return queryset
    

class CartTotalView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        user_id = self.kwargs.get('user_id')  # Use get() method to handle the case where user_id is not present

        
        if user_id is not None:
            user = User.objects.get(id=user_id)
            queryset = Cart.objects.filter(cart_id=cart_id, user=user)
        else:
            queryset = Cart.objects.filter(cart_id=cart_id)
        
        return queryset
    

class CartDetailView(generics.RetrieveAPIView):
    # Define the serializer class for the view
    serializer_class = CartSerializer
    # Specify the lookup field for retrieving objects using 'cart_id'
    lookup_field = 'cart_id'

    # Add a permission class for the view
    permission_classes = (AllowAny,)


    def get_queryset(self):
        # Get 'cart_id' and 'user_id' from the URL kwargs
        cart_id = self.kwargs['cart_id']
        user_id = self.kwargs.get('user_id')  # Use get() to handle cases where 'user_id' is not present

        if user_id is not None:
            # If 'user_id' is provided, filter the queryset by both 'cart_id' and 'user_id'
            user = User.objects.get(id=user_id)
            queryset = Cart.objects.filter(cart_id=cart_id, user=user)
        else:
            # If 'user_id' is not provided, filter the queryset by 'cart_id' only
            queryset = Cart.objects.filter(cart_id=cart_id)

        return queryset

    def get(self, request, *args, **kwargs):
        # Get the queryset of cart items based on 'cart_id' and 'user_id' (if provided)
        queryset = self.get_queryset()

        # Initialize sums for various cart item attributes
        total_shipping = 0.0
        total_tax = 0.0
        total_service_fee = 0.0
        total_sub_total = 0.0
        total_total = 0.0

        # Iterate over the queryset of cart items to calculate cumulative sums
        for cart_item in queryset:
            # Calculate the cumulative shipping, tax, service_fee, and total values
            total_shipping += float(self.calculate_shipping(cart_item))
            total_tax += float(self.calculate_tax(cart_item))
            total_service_fee += float(self.calculate_service_fee(cart_item))
            total_sub_total += float(self.calculate_sub_total(cart_item))
            total_total += round(float(self.calculate_total(cart_item)), 2)

        # Create a data dictionary to store the cumulative values
        data = {
            'shipping': round(total_shipping, 2),
            'tax': total_tax,
            'service_fee': total_service_fee,
            'sub_total': total_sub_total,
            'total': total_total,
        }

        # Return the data in the response
        return Response(data)

    def calculate_shipping(self, cart_item):
        # Implement your shipping calculation logic here for a single cart item
        # Example: Calculate based on weight, destination, etc.
        return cart_item.shipping_amount

    def calculate_tax(self, cart_item):
        # Implement your tax calculation logic here for a single cart item
        # Example: Calculate based on tax rate, product type, etc.
        return cart_item.tax_fee

    def calculate_service_fee(self, cart_item):
        # Implement your service fee calculation logic here for a single cart item
        # Example: Calculate based on service type, cart total, etc.
        return cart_item.service_fee

    def calculate_sub_total(self, cart_item):
        # Implement your service fee calculation logic here for a single cart item
        # Example: Calculate based on service type, cart total, etc.
        return cart_item.sub_total

    def calculate_total(self, cart_item):
        # Implement your total calculation logic here for a single cart item
        # Example: Sum of sub_total, shipping, tax, and service_fee
        return cart_item.total
    


class CartItemDeleteView(generics.DestroyAPIView):
    serializer_class = CartSerializer
    lookup_field = 'cart_id'  

    def get_object(self):
        cart_id = self.kwargs['cart_id']
        item_id = self.kwargs['item_id']
        user_id = self.kwargs.get('user_id')

        if user_id is not None:
            user = get_object_or_404(User, id=user_id)
            cart = get_object_or_404(Cart, cart_id=cart_id, id=item_id, user=user)
        else:
            cart = get_object_or_404(Cart, cart_id=cart_id, id=item_id)

        return cart
    

class CreateOrderView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer
    queryset = CartOrder.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        payload = request.data

        full_name = payload['full_name']
        email = payload['email']
        mobile = payload['mobile']
        address = payload['address']
        city = payload['city']
        state = payload['state']
        country = payload['country']
        cart_id = payload['cart_id']
        user_id = payload['user_id']

        print("user_id ===============", user_id)

        if user_id != 0:
            user = User.objects.filter(id=user_id).first()
        else:
            user = None

        cart_items = Cart.objects.filter(cart_id=cart_id)

        total_shipping = Decimal(0.0)
        total_tax = Decimal(0.0)
        total_service_fee = Decimal(0.0)
        total_sub_total = Decimal(0.0)
        total_initial_total = Decimal(0.0)
        total_total = Decimal(0.0)

        with transaction.atomic():

            order = CartOrder.objects.create(
                # sub_total=total_sub_total,
                # shipping_amount=total_shipping,
                # tax_fee=total_tax,
                # service_fee=total_service_fee,
                buyer=user,
                payment_status="processing",
                full_name=full_name,
                email=email,
                mobile=mobile,
                address=address,
                city=city,
                state=state,
                country=country
            )

            for c in cart_items:
                CartOrderItem.objects.create(
                    order=order,
                    product=c.product,
                    qty=c.qty,
                    color=c.color,
                    size=c.size,
                    price=c.price,
                    sub_total=c.sub_total,
                    shipping_amount=c.shipping_amount,
                    tax_fee=c.tax_fee,
                    service_fee=c.service_fee,
                    total=c.total,
                    initial_total=c.total,
                    vendor=c.product.vendor
                )

                total_shipping += Decimal(c.shipping_amount)
                total_tax += Decimal(c.tax_fee)
                total_service_fee += Decimal(c.service_fee)
                total_sub_total += Decimal(c.sub_total)
                total_initial_total += Decimal(c.total)
                total_total += Decimal(c.total)

                order.vendor.add(c.product.vendor)

                

            order.sub_total=total_sub_total
            order.shipping_amount=total_shipping
            order.tax_fee=total_tax
            order.service_fee=total_service_fee
            order.initial_total=total_initial_total
            order.total=total_total

            
            order.save()

        return Response( {"message": "Order Created Successfully", 'order_oid':order.oid}, status=status.HTTP_201_CREATED)




class CheckoutView(generics.RetrieveAPIView):
    serializer_class = CartOrderSerializer
    lookup_field = 'order_oid'  

    def get_object(self):
        order_oid = self.kwargs['order_oid']
        cart = get_object_or_404(CartOrder, oid=order_oid)
        return cart
    

class CouponApiView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer

    def create(self, request, *args, **kwargs):
        payload = request.data

        order_oid = payload['order_oid']
        coupon_code = payload['coupon_code']
        print("order_oid =======", order_oid)
        print("coupon_code =======", coupon_code)

        order = CartOrder.objects.get(oid=order_oid)
        coupon = Coupon.objects.filter(code__iexact=coupon_code, active=True).first()
        
        if coupon:
            order_items = CartOrderItem.objects.filter(order=order, vendor=coupon.vendor)
            if order_items:
                for i in order_items:
                    print("order_items =====", i.product.title)
                    if not coupon in i.coupon.all():
                        discount = i.total * coupon.discount / 100
                        
                        i.total -= discount
                        i.sub_total -= discount
                        i.coupon.add(coupon)
                        i.saved += discount
                        i.applied_coupon = True

                        order.total -= discount
                        order.sub_total -= discount
                        order.saved += discount

                        i.save()
                        order.save()
                        return Response( {"message": "Coupon Activated"}, status=status.HTTP_200_OK)
                    else:
                        return Response( {"message": "Coupon Already Activated"}, status=status.HTTP_200_OK)
            return Response( {"message": "Order Item Does Not Exists"}, status=status.HTTP_200_OK)
        else:
            return Response( {"message": "Coupon Does Not Exists"}, status=status.HTTP_404_NOT_FOUND)


    


class StripeCheckoutView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer

    def create(self, request, *args, **kwargs):
        order_oid = self.kwargs['order_oid']
        order = CartOrder.objects.filter(oid=order_oid).first()

        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=order.email,
                payment_method_types=['card'],
                metadata={
                    'order_oid': order.oid,
                },
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': order.full_name,
                            },
                            'unit_amount': int(order.total * 100),
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                # success_url = f"{settings.SITE_URL}/payment-success/{{order.oid}}/?session_id={{CHECKOUT_SESSION_ID}}",
                # cancel_url = f"{settings.SITE_URL}/payment-success/{{order.oid}}/?session_id={{CHECKOUT_SESSION_ID}}",

                success_url=settings.SITE_URL+'/payment-success/'+ order.oid +'?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.SITE_URL+'/?session_id={CHECKOUT_SESSION_ID}',
            )
            order.stripe_session_id = checkout_session.id 
            order.save()

            return redirect(checkout_session.url)
        except stripe.error.StripeError as e:
            return Response( {'error': f'Something went wrong when creating stripe checkout session: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@transaction.atomic
def finalize_order_payment(order):
    order_items = CartOrderItem.objects.select_related('vendor').filter(order=order)

    if order.payment_status != "processing":
        return

    order.payment_status = "paid"
    order.save()

    try:
        if order.buyer != None:
            send_notification(user=order.buyer, order=order)

        for o in order_items:
            send_notification(vendor=o.vendor, order=order, order_item=o)
    except Exception:
        pass

    try:
        merge_data = {
            'order': order,
            'order_items': order_items,
        }

        subject = f"Order Placed Successfully"
        text_body = render_to_string("email/customer_order_confirmation.txt", merge_data)
        html_body = render_to_string("email/customer_order_confirmation.html", merge_data)

        msg = EmailMultiAlternatives(
            subject=subject, from_email=settings.FROM_EMAIL,
            to=[order.email], body=text_body
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()

        for o in order_items:
            subject = f"New Sale!"
            text_body = render_to_string("email/vendor_order_sale.txt", merge_data)
            html_body = render_to_string("email/vendor_order_sale.html", merge_data)

            msg = EmailMultiAlternatives(
                subject=subject, from_email=settings.FROM_EMAIL,
                to=[o.vendor.email], body=text_body
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()
    except Exception:
        pass


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        if not settings.STRIPE_WEBHOOK_SECRET:
            return HttpResponse(status=500)

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.STRIPE_WEBHOOK_SECRET,
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return HttpResponse(status=400)

        try:
            event_type = event.get('type')
            if event_type == 'checkout.session.completed':
                session = event['data']['object']
                if session.get('payment_status') == 'paid':
                    with transaction.atomic():
                        order_oid = (session.get('metadata') or {}).get('order_oid')
                        order = None
                        if order_oid:
                            order = CartOrder.objects.select_for_update().filter(oid=order_oid).first()
                        if not order:
                            order = CartOrder.objects.select_for_update().filter(stripe_session_id=session.get('id')).first()
                        if order and order.payment_status == 'processing':
                            finalize_order_payment(order)
        except Exception:
            return HttpResponse(status=200)

        return HttpResponse(status=200)


class PaymentSuccessView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer
    queryset = CartOrder.objects.all()
    
    
    def create(self, request, *args, **kwargs):
        payload = request.data
        
        order_oid = payload['order_oid']
        session_id = payload['session_id']

        order = CartOrder.objects.get(oid=order_oid)
        if order.payment_status == "paid":
            return Response({"message": "Payment Successfull"}, status=status.HTTP_200_OK)

        if order.payment_status != "processing":
            return Response({"message": "An Error Occured!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if session_id == "null":
            return Response({"message": "Pending"}, status=status.HTTP_202_ACCEPTED)

        return Response({"message": "Pending"}, status=status.HTTP_202_ACCEPTED)


class ReviewRatingAPIView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (AllowAny, )

    def create(self, request, *args, **kwargs):
        payload = request.data

        user_id = payload['user_id']
        product_id = payload['product_id']
        rating = payload['rating']
        review = payload['review']

        user = User.objects.get(id=user_id)
        product = Product.objects.get(id=product_id)

        Review.objects.create(user=user, product=product, rating=rating, review=review)
    
        return Response( {"message": "Review Created Successfully."}, status=status.HTTP_201_CREATED)



class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (AllowAny, )

    def get_queryset(self):
        product_id = self.kwargs['product_id']

        from django.shortcuts import get_object_or_404

        product = get_object_or_404(Product, id=product_id)
        return Review.objects.filter(product=product)
    
class SearchProductsAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        query = self.request.GET.get('query')
        print("query =======", query)

        products = Product.objects.filter(status="published", title__icontains=query)
        return products
       