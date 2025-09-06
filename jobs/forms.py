from django import forms


PLATFORMS = (
    ("glassdoor", "Glassdoor"),
    ("indeed", "Indeed"),
)


class ScrapeForm(forms.Form):
    platform = forms.ChoiceField(choices=PLATFORMS, initial="indeed")
    role_name = forms.CharField(
        max_length=100, 
        initial="Software Engineer",
        help_text="Enter the job role you want to search for (e.g., Data Science, Software Engineer, Product Manager)"
    )
    location = forms.CharField(
        max_length=100,
        initial="New York, NY",
        help_text="Enter the location to search in (e.g., New York, NY, San Francisco, CA, Remote)"
    )
    limit = forms.IntegerField(min_value=1, max_value=100, initial=20, help_text="Number of jobs to scrape (1-100)")
