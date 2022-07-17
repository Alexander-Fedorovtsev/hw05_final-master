from django.views.generic import CreateView
from django.urls import reverse_lazy


from .forms import CreatonForm


class SignUp(CreateView):
    form_class = CreatonForm
    # Куда переадресовать пользователя после того, как он отправит форму
    succes_url = reverse_lazy("posts:index")
    # Какой шаблон применить для отображения веб-формы
    template_name = "users/signup.html"
