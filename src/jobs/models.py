from django.db import models
from django.db.models.signals import pre_save, post_save
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from ckeditor.fields import RichTextField

from accounts.models import Company, Industry, Applicant

User = settings.AUTH_USER_MODEL

JOB_TYPES = (
        ('fulltime', 'Full-Time'),
        ('parttime', 'Part-Time')
    )

MIN_QUALIFICATIONS = (
    ('ssce', 'SSCE'),
    ('bsc', 'BSc'),
    ('msc', 'MSc'),
    ('phd', 'PhD')
)

YEARS_OF_EXP = (
    ('entry', 'Entry Level'),
    ('1-2', '1-2 years'),
    ('3-5', '3-5 years'),
    ('6-10', '6-10 years'),
    ('above 10', 'Above 10 years')
)

Job_Status = (
    ('posted','Job Posted'),
    ('saved', 'Saved but unposted'),
    ('unsaved', 'Unsaved')
)

class Job(models.Model):
    title               = models.CharField(max_length=60)
    slug                = models.SlugField(blank=True)
    industry            = models.ForeignKey(Industry, on_delete=models.SET_NULL, blank=True, null=True)
    company             = models.ForeignKey(Company, on_delete=models.CASCADE)
    job_type            = models.CharField(max_length=10, choices=JOB_TYPES)
    min_qualification   = models.CharField('Minimum Qualification', max_length=10, choices=MIN_QUALIFICATIONS, null=True, blank=True)
    years_of_exp        = models.CharField('Years of Experience', max_length=20, choices=YEARS_OF_EXP, null=True, blank=True)
    salary              = models.PositiveIntegerField(blank=True, null=True)
    description         = RichTextField()
    # expires_on = models.DateTimeField()
    # Job_status          = models.CharField(max_length=30, choices = Job_Status)
    posted_on           = models.DateTimeField(auto_now_add=True)
    updated_on          = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Job, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('job', kwargs={'slug': self.slug})


APPLICATION_STATUS = (
    ('applied', 'Applied'),
    ('shortlisted', 'Shortlisted'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected')
)

class ApplicationManager(models.Manager):

    def has_applied(self, user, job):
        applied = False
        msg = 'Thanks for your Application'
        if user.is_applicant:
            applicant = user.applicant
            qs = self.get_queryset().filter(job=job, applicant=applicant)
            if qs.exists():
                applied = True
                msg = 'You have previously applied for this job'
        else:
            msg = 'You are not eligible to apply for this job'
        return applied, msg

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/documents/user_<id>/<filename>
    return 'documents/user_{0}/{1}'.format(instance.applicant.user.id, filename)

class Application(models.Model):
    applicant       = models.ForeignKey(Applicant, on_delete=models.CASCADE, blank=True, null=True)
    job             = models.ForeignKey(Job, on_delete=models.CASCADE, blank=True, null=True)
    applied_on      = models.DateTimeField(auto_now_add=True)
    status          = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='applied')
    # add resume and cover letter
    resume          = models.FileField(upload_to=user_directory_path, null=True)
    cover_letter    = models.TextField(max_length=100, null=True)


    objects = ApplicationManager()

    def __str__(self):
        return self.applicant.user.full_name
