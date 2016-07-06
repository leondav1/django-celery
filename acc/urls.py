from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    url('', include('django.contrib.auth.urls')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^payments$', login_required(TemplateView.as_view(template_name='payments.html')), name='payments'),
]
