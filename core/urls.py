from django.urls import path
from django.views.generic import TemplateView

# URLConf
urlpatterns = [
    path('', TemplateView.as_view(template_name='core/index.html'))
]
