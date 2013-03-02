from content_profiles.models import ContentProfile
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Submit, Fieldset, Layout, HTML
from tinymce.widgets import TinyMCE
from django import forms
from crispy_forms.helper import FormHelper

class ContentProfileAddForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30,"class":"span9"}))
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(
                'Add new profile',
                'url'
            ),
            FormActions(
                Submit('submit', 'Submit', css_class='button btn-primary')
            )
        )
        super(ContentProfileAddForm, self).__init__(*args, **kwargs)
        
        # Gets around the fact that name & content are part of the model, but 
        # aren't part of the form.
        # Too hacky?
        for key in self.fields:
            self.fields[key].required = False
    class Meta:
        model = ContentProfile