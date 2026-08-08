from django import forms
from .models import PG

class PGForm(forms.ModelForm):
    availability = forms.ChoiceField(
        choices=[
            ('available', 'Available'),
            ('booked', 'Booked'),
            ('coming_soon', 'Coming Soon'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select form-control-lg form-control-custom rounded-3 shadow-sm availability-select',
            'style': 'color: #f8fafc !important; background: rgba(255,255,255,0.12) !important; border: 2px solid var(--primary-color) !important; font-weight: 600; font-size: 1.1rem; min-height: 56px;'
        }),
        required=True,
    )

    class Meta:
        model = PG
        fields = [
            'name',
            'location',
            'price',
            'description',
            'phone',
            'owner_email',
            'is_wifi',
            'is_ac',
            'is_food',
            'availability'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg form-control-custom rounded-3 shadow-sm'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control form-control-lg form-control-custom rounded-3 shadow-sm'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg form-control-custom rounded-3 shadow-sm',
                'inputmode': 'numeric',
                'placeholder': '7500',
                'min': '1000',
                'step': '500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-custom rounded-3 shadow-sm',
                'rows': 4,
                'placeholder': 'Describe your property, amenities, rules, nearby facilities...'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg form-control-custom rounded-3 shadow-sm',
                'placeholder': '+91 9876543210'
            }),
            'owner_email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg form-control-custom rounded-3 shadow-sm'
            }),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 500:
            raise forms.ValidationError('Price must be at least ₹500')
        if price and price > 200000:
            raise forms.ValidationError('Price seems too high.')
        return price

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            cleaned = phone.replace(' ', '').replace('-', '').replace('+', '')
            if not cleaned.isdigit():
                raise forms.ValidationError('Phone must contain only digits.')
            if len(cleaned) < 10:
                raise forms.ValidationError('Phone number must be at least 10 digits.')
        return phone

    labels = {
        'name': '',
        'price': '',
        'location': '',
        'description': '',
        'phone': '',
        'owner_email': '',
    }
    help_texts = {
        'availability': 'This status appears on public listings',
    }
