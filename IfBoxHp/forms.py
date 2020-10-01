from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"]="form-control"
        self.fields["password1"].widget.attrs["class"]="form-control"
        self.fields["password2"].widget.attrs["class"]="form-control"


