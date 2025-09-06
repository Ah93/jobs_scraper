def create_test_jobs(limit: int = 5):
    """
    Create some test jobs for debugging purposes.
    This bypasses web scraping to test the database saving functionality.
    """
    test_jobs = []
    
    for i in range(limit):
        job = {
            "title": f"Test Software Engineer {i+1}",
            "company": f"Test Company {i+1}",
            "location": f"Test City {i+1}",
            "description": f"This is a test job description for position {i+1}. This job involves software development and testing.",
            "source_url": f"https://test-job-{i+1}.com",
            "platform": "glassdoor"
        }
        test_jobs.append(job)
    
    return test_jobs
