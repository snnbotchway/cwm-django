from . import views
from django.urls import path

urlpatterns = [
    path('products/', views.product_list),
    path('products/<int:id>/', views.product),
    path('categories/<int:pk>/', views.category, name='category_detail'),
    path('categories/', views.category_list, name='category_list'),
    # path('products/new/', views.contactCreate),
    # path('contact-edit/<int:pk>', views.contactEdit),
    # path('contact-delete/<int:pk>', views.contactDelete),
    # path('upload-csv/', views.uploadCsv),
]
