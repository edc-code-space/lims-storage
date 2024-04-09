from django import forms

from storage_module.models import *


class MoveSampleForm(forms.Form):
    box = forms.ModelChoiceField(queryset=DimBox.objects.all(),
                                 widget=forms.Select(attrs={"class": "select2"}))
    x_position = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    y_position = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(MoveSampleForm, self).__init__(*args, **kwargs)
        self.fields['box'].label_from_instance = lambda obj: "{}".format(obj.box_name)


class MoveBoxForm(forms.Form):
    freezer = forms.ModelChoiceField(
        queryset=DimFreezer.objects.all(),
        widget=forms.Select(attrs={"class": "select2"}),
    )
    shelf = forms.ModelChoiceField(queryset=DimShelf.objects.all(),
                                   required=False,
                                   widget=forms.Select(attrs={"class": "select2"}))
    rack = forms.ModelChoiceField(queryset=DimRack.objects.all(),
                                  required=False,
                                  widget=forms.Select(attrs={"class": "select2"}))

    def __init__(self, *args, **kwargs):
        super(MoveBoxForm, self).__init__(*args, **kwargs)
        self.fields['rack'].label_from_instance = lambda obj: "{}".format(obj.rack_name)
        self.fields['shelf'].label_from_instance = lambda obj: "{}".format(obj.shelf_name)
        self.fields['freezer'].label_from_instance = lambda obj: "{}".format(
            obj.freezer_name)
