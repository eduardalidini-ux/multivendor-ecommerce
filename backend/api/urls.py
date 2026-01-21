from django.urls import path, include
from userauths import views as userauths_views
from store import views as store_views
from customer import views as customer_views
from vendor import views as vendor_views
from api import storage_views

from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('', userauths_views.getRoutes),

    path('warehouse/', include('warehouse.urls')),

    # Storage (Supabase S3-compatible) helper endpoints
    path('storage/presign-upload/', storage_views.PresignUploadView.as_view(), name='storage-presign-upload'),
    path('storage/presign-download/', storage_views.PresignDownloadView.as_view(), name='storage-presign-download'),
    path('storage/debug-s3/', storage_views.DebugS3View.as_view(), name='storage-debug-s3'),

    # Userauths API Endpoints
    path('user/token/', userauths_views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', userauths_views.RegisterView.as_view(), name='auth_register'),
    path('user/profile/<int:user_id>/', userauths_views.ProfileView.as_view(), name='user_profile'),
    path('user/test/', userauths_views.testEndPoint, name='auth_register'),
    path('user/password-reset/<str:email>/', userauths_views.PasswordEmailVerify.as_view(), name='password_reset'),
    path('user/password-change/', userauths_views.PasswordChangeView.as_view(), name='password_reset'),

    # Adoon Endpoint
    path('addon/', store_views.ConfigSettingsDetailView.as_view(), name='addon'),


    # Store API Endpoints
    path('category/', store_views.CategoryListView.as_view(), name='category'),
    path('brand/', store_views.BrandListView.as_view(), name='brand'),
    path('products/', store_views.ProductListView.as_view(), name='products'),
    path('featured-products/', store_views.FeaturedProductListView.as_view(), name='featured-products'),
    path('products/<slug:slug>/', store_views.ProductDetailView.as_view(), name='brand'),
    path('cart-view/', store_views.CartApiView.as_view(), name='cart-view'),
    path('cart-list/<str:cart_id>/', store_views.CartListView.as_view(), name='cart-list'),
    path('cart-list/<str:cart_id>/<int:user_id>/', store_views.CartListView.as_view(), name='cart-list-with-user'),
    path('cart-detail/<str:cart_id>/', store_views.CartDetailView.as_view(), name='cart-detail'),
    path('cart-detail/<str:cart_id>/<int:user_id>/', store_views.CartDetailView.as_view(), name='cart-detail'),
    path('cart-delete/<str:cart_id>/<int:item_id>/', store_views.CartItemDeleteView.as_view(), name='cart-delete'),
    path('cart-delete/<str:cart_id>/<int:item_id>/<int:user_id>/', store_views.CartItemDeleteView.as_view(), name='cart-delete'),
    path('create-order/', store_views.CreateOrderView.as_view(), name='cart-delete'),
    path('checkout/<str:order_oid>/', store_views.CheckoutView.as_view(), name='checkout'),
    path('coupon/', store_views.CouponApiView.as_view(), name='coupon'),
    path('create-review/', store_views.ReviewRatingAPIView.as_view(), name='create-review'),
    path('reviews/<int:product_id>/', store_views.ReviewListView.as_view(), name='create-review'),
    path('search/', store_views.SearchProductsAPIView.as_view(), name='search'),

    # Payment
    path('stripe-checkout/<str:order_oid>/', store_views.StripeCheckoutView.as_view(), name='stripe-checkout'),
    path('stripe/webhook/', store_views.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('payment-success/', store_views.PaymentSuccessView.as_view(), name='payment-success'),

    # Customer API Endpoints
    path('customer/orders/<int:user_id>/', customer_views.OrdersAPIView.as_view(), name='customer-orders'),
    path('customer/order/detail/<int:user_id>/<str:order_oid>/', customer_views.OrdersDetailAPIView.as_view(), name='customer-order-detail'),
    path('customer/wishlist/create/', customer_views.WishlistCreateAPIView.as_view(), name='customer-wishlist-create'),
    path('customer/wishlist/<int:user_id>/', customer_views.WishlistAPIView.as_view(), name='customer-wishlist'),
    path('customer/notification/<int:user_id>/', customer_views.CustomerNotificationView.as_view(), name='customer-notification'),
    path('customer/setting/<int:pk>/', customer_views.CustomerUpdateView.as_view(), name='customer-settings'),

    # Vendor API Endpoints
    path('vendor/stats/<int:vendor_id>/', vendor_views.DashboardStatsAPIView.as_view(), name='vendor-stats'),
    path('vendor/products/<int:vendor_id>/', vendor_views.ProductsAPIView.as_view(), name='vendor-prdoucts'),
    path('vendor/orders/<int:vendor_id>/', vendor_views.OrdersAPIView.as_view(), name='vendor-orders'),
    path('vendor/orders/<int:vendor_id>/<str:order_oid>/', vendor_views.OrderDetailAPIView.as_view(), name='vendor-order-detail'),
    path('vendor/yearly-report/<int:vendor_id>/', vendor_views.YearlyOrderReportChartAPIView.as_view(), name='vendor-yearly-report'),
    path('vendor-orders-report-chart/<int:vendor_id>/', vendor_views.MonthlyOrderChartAPIFBV, name='vendor-orders-report-chart'),
    path('vendor-products-report-chart/<int:vendor_id>/', vendor_views.MonthlyProductsChartAPIFBV, name='vendor-product-report-chart'),
    path('vendor-product-create/<int:vendor_id>/', vendor_views.ProductCreateView.as_view(), name='vendor-product-create'),
    path('vendor-product-edit/<int:vendor_id>/<str:product_pid>/', vendor_views.ProductUpdateAPIView.as_view(), name='vendor-product-edit'),
    path('vendor-product-delete/<int:vendor_id>/<str:product_pid>/', vendor_views.ProductDeleteAPIView.as_view(), name='vendor-product-delete'),
    path('vendor-product-filter/<int:vendor_id>/', vendor_views.FilterProductsAPIView.as_view(), name='vendor-product-filter'),
    path('vendor-earning/<int:vendor_id>/', vendor_views.Earning.as_view(), name='vendor-product-filter'),
    path('vendor-monthly-earning/<int:vendor_id>/', vendor_views.MonthlyEarningTracker, name='vendor-product-filter'),
    path('vendor-reviews/<int:vendor_id>/', vendor_views.ReviewsListAPIView.as_view(), name='vendor-reviews'),
    path('vendor-reviews/<int:vendor_id>/<int:review_id>/', vendor_views.ReviewsDetailAPIView.as_view(), name='vendor-review-detail'),
    path('vendor-coupon-list/<int:vendor_id>/', vendor_views.CouponListAPIView.as_view(), name='vendor-coupon-list'),
    path('vendor-coupon-stats/<int:vendor_id>/', vendor_views.CouponStats.as_view(), name='vendor-coupon-stats'),
    path('vendor-coupon-detail/<int:vendor_id>/<int:coupon_id>/', vendor_views.CouponDetailAPIView.as_view(), name='vendor-coupon-detail'),
    path('vendor-coupon-create/<int:vendor_id>/', vendor_views.CouponCreateAPIView.as_view(), name='vendor-coupon-create'),
    path('vendor-notifications-unseen/<int:vendor_id>/', vendor_views.NotificationUnSeenListAPIView.as_view(), name='vendor-notifications-list'),
    path('vendor-notifications-seen/<int:vendor_id>/', vendor_views.NotificationSeenListAPIView.as_view(), name='vendor-notifications-list'),
    path('vendor-notifications-summary/<int:vendor_id>/', vendor_views.NotificationSummaryAPIView.as_view(), name='vendor-notifications-summary'),
    path('vendor-notifications-mark-as-seen/<int:vendor_id>/<int:noti_id>/', vendor_views.NotificationMarkAsSeen.as_view(), name='vendor-notifications-mark-as-seen'),
    path('vendor-settings/<int:pk>/', vendor_views.VendorProfileUpdateView.as_view(), name='vendor-settings'),
    path('vendor-shop-settings/<int:pk>/', vendor_views.ShopUpdateView.as_view(), name='customer-settings'),
    path('shop/<slug:vendor_slug>/', vendor_views.ShopAPIView.as_view(), name='shop'),
    path('vendor-products/<slug:vendor_slug>/', vendor_views.ShopProductsAPIView.as_view(), name='vendor-products'),
    path('vendor-register/', vendor_views.VendorRegister.as_view(), name='vendor-register'),

    # Tracking Feature
    path('vendor/couriers/', vendor_views.CourierListAPIView.as_view()),
    path('vendor/order-item-detail/<int:pk>/', vendor_views.OrderItemDetailAPIView.as_view()),

    

]