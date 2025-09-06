from django.db import models
from django.utils.text import slugify


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    PLATFORM_CHOICES = [
        ("indeed", "Indeed"),
        ("glassdoor", "Glassdoor"),
    ]

    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    description = models.TextField(blank=True)
    # A canonical/first source URL to view the job
    source_url = models.URLField()
    # All platforms where we found it (CSV/JSON field)
    sources = models.JSONField(default=list)
    # Hash used for dedupe: normalized(title+company+location)
    fingerprint = models.CharField(max_length=255, db_index=True)
    posted_at = models.DateTimeField(blank=True, null=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("fingerprint", "company")

    def __str__(self):
        return f"{self.title} @ {self.company.name} ({self.location})"