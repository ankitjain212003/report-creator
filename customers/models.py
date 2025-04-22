from django.db import models

class Company(models.Model):
    CATEGORY_CHOICES = [
        ('central_ministry', 'Central Ministry/Department'),
        ('govt_org', 'Organisation under Government Development'),
        ('private_sector', 'Private Sector'),
        ('public_sector', 'Public Sector'),
        ('state_govt', 'State Government Department'),
    ]

    SECTOR_CHOICES = [
        ('agriculture', 'Agriculture'),
        ('defence', 'Defence'),
        ('education', 'Education'),
        ('energy', 'Energy'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('inf_broadcasting', 'Information and Broadcasting'),
        ('inf_communication', 'Information and Communication Technology'),
    ]

   
    img = models.ImageField(upload_to='company')
    address = models.TextField()
    internal = models.BooleanField(default=False)
    name = models.CharField(max_length=300,unique = True)

    
    hash_value = models.CharField(max_length=100, blank=True, null=True)
    receive_date = models.DateField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES, blank=True, null=True)

    def get_full_image_url(self):
        if self.img and hasattr(self.img, 'url'):
            return self.img.url
        return None

    def delete(self, *args, **kwargs):
        if not self.internal:
            super(Company, self).delete(*args, **kwargs)
        else:
            print(f"Attempt to delete internal company '{self.name}' ignored.")
