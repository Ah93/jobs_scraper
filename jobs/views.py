from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
import csv
from .forms import ScrapeForm
from .scraper.pipeline import run_scrape_pipeline
from .scraper.progress import ProgressTracker, get_progress
from .models import Job




def dashboard(request):
    form = ScrapeForm()
    # Don't show recent jobs by default - let user search for specific roles
    jobs = []
    return render(request, 'jobs/dashboard.html', {"form": form, "jobs": jobs})


def run_scrape(request):
    if request.method == 'POST':
        form = ScrapeForm(request.POST)
        if form.is_valid():
            platform = form.cleaned_data['platform']
            role_name = form.cleaned_data['role_name']
            location = form.cleaned_data['location']
            limit = form.cleaned_data['limit']
            
            # Generate operation ID for progress tracking
            operation_id = str(uuid.uuid4())
            progress = ProgressTracker(operation_id)
            
            print(f"Starting scrape: platform={platform}, role={role_name}, location={location}, limit={limit}")
            print(f"Operation ID: {operation_id}")
            
            try:
                # Clear previous jobs for this platform before new search
                print(f"Clearing previous {platform} jobs before new search...")
                all_jobs = Job.objects.all()
                jobs_to_delete = [job for job in all_jobs if platform in job.sources]
                for job in jobs_to_delete:
                    job.delete()
                print(f"Cleared {len(jobs_to_delete)} previous {platform} jobs")
                
                # Update progress
                progress.update("initializing", 0, 100, f"Starting scrape for '{role_name}' jobs in '{location}'...")
                
                # Run the scrape pipeline
                count = run_scrape_pipeline(platform, role_name, limit, location, progress)
                
                # Mark as complete
                progress.complete(f"Scrape complete. Added/merged {count} jobs.")
                
                print(f"Scrape completed with {count} jobs")
                
                # Show search results after successful scrape
                if count > 0:
                    # Get the most recent jobs for this search (SQLite compatible)
                    all_jobs = Job.objects.all().order_by('-scraped_at')
                    recent_jobs = [job for job in all_jobs if platform in job.sources][:50]
                    return render(request, 'jobs/dashboard.html', {
                        "form": ScrapeForm(),
                        "jobs": recent_jobs,
                        "search_role": role_name,
                        "search_location": location,
                        "search_platform": platform
                    })
                
            except Exception as e:
                progress.error(f"Scrape failed: {str(e)}")
                print(f"Scrape failed: {e}")
                messages.error(request, f"Scrape failed: {str(e)}")
            
            finally:
                # Clean up progress file after a delay
                import threading
                def cleanup():
                    import time
                    time.sleep(10)  # Keep progress for 10 seconds
                    progress.cleanup()
                
                threading.Thread(target=cleanup).start()
            
            return redirect('jobs:dashboard')
        else:
            print(f"Form validation failed: {form.errors}")
            messages.error(request, "Form validation failed.")
            return redirect('jobs:dashboard')

@csrf_exempt
def get_scrape_progress(request, operation_id):
    """Get progress for a scraping operation"""
    if request.method == 'GET':
        progress_data = get_progress(operation_id)
        return JsonResponse(progress_data)
    return JsonResponse({"error": "Method not allowed"}, status=405)

def clear_jobs(request):
    """Clear all jobs from the database"""
    if request.method == 'POST':
        try:
            Job.objects.all().delete()
            from .models import Company
            Company.objects.all().delete()
            messages.success(request, "All jobs and companies cleared successfully!")
        except Exception as e:
            messages.error(request, f"Error clearing jobs: {str(e)}")
    return redirect('jobs:dashboard')


def download_csv(request):
    """Download jobs as CSV file"""
    if request.method == 'GET':
        try:
            # Get the platform from request parameters
            platform = request.GET.get('platform', 'all')
            
            # Get jobs based on platform filter
            if platform == 'all':
                jobs = Job.objects.all().order_by('-scraped_at')
            else:
                all_jobs = Job.objects.all().order_by('-scraped_at')
                jobs = [job for job in all_jobs if platform in job.sources]
            
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="jobs_{platform}_{platform if platform != "all" else "all"}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Job Title', 'Company Name', 'Job Location', 'Job Description', 'Source URL', 'Sources', 'Scraped At'])
            
            for job in jobs:
                sources_str = ', '.join(job.sources) if job.sources else ''
                writer.writerow([
                    job.title,
                    job.company.name,
                    job.location,
                    job.description,
                    job.source_url,
                    sources_str,
                    job.scraped_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            return response
            
        except Exception as e:
            messages.error(request, f"Error generating CSV: {str(e)}")
            return redirect('jobs:dashboard')
    
    return redirect('jobs:dashboard')

def get_latest_jobs(request):
    """Get the latest jobs for real-time display"""
    if request.method == 'GET':
        try:
            # Get the platform from request parameters
            platform = request.GET.get('platform', 'indeed')
            
            # Get the most recent jobs for the current platform (SQLite compatible)
            all_jobs = Job.objects.all().order_by('-scraped_at')
            jobs = [job for job in all_jobs if platform in job.sources][:50]
            
            jobs_data = []
            for job in jobs:
                jobs_data.append({
                    'id': job.id,
                    'title': job.title,
                    'company': job.company.name,
                    'location': job.location,
                    'sources': job.sources,
                    'source_url': job.source_url,
                    'scraped_at': job.scraped_at.strftime('%Y-%m-%d %H:%M')
                })
            
            return JsonResponse({
                'success': True,
                'jobs': jobs_data,
                'count': len(jobs_data)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)