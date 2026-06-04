from django.db import models

class DonationMethod(models.Model):
    method_name = models.CharField(max_length=100, help_text='e.g., bKash, Bank Transfer')
    account_details = models.TextField(help_text='Account number or routing info')
    instructions = models.TextField(blank=True, help_text='Any specific instructions for the donor')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.method_name
