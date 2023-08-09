import uuid
from django.db import models
from accountapp.models import User as UserAuth

def hex_uuid():
    return uuid.uuid4().hex


class Company(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    about = models.TextField(max_length=500)
    company_id = models.UUIDField(
        primary_key=True, default=hex_uuid, editable=False
    )  # uuid1 uses network address for random number, so it's better to use uuid4

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'tbl_company'


class Job(models.Model):
    job_id = models.UUIDField(primary_key=True, default=hex_uuid, editable=False)
    job_role = models.CharField(max_length=100, null=False)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="companyies", null=False
    )
    description = models.TextField(default="No description provided", max_length=500)
    location = models.CharField(max_length=100)
    post_date = models.DateField(null=False)
    posted = models.BooleanField(default=False, null=False)
    experience = models.IntegerField(default=0, null=False)
    created_at = models.DateTimeField(auto_now_add=True)  # only add the timestamp once
    updated_at = models.DateTimeField(auto_now=True)  # update timestamp on every save()

    def __str__(self):
        return self.job_role
    
    class Meta:
        db_table = 'tbl_job'


class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=hex_uuid, editable=False)
    name = models.CharField(max_length=30, null=False)
    email = models.CharField(max_length=30, null=False)
    address = models.TextField(max_length=100, null=False)
    phone = models.CharField(max_length=12, default=None,null=True)
    about = models.TextField(max_length=100, default=None)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=False)
    uid = models.ForeignKey(UserAuth, on_delete=models.CASCADE)

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=False
    )

    class Meta:
        db_table = 'tbl_user_profile'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.resume:
            self.resume_file_path = self.resume.path
        else:
            self.resume_file_path = ""
        super().save(*args, **kwargs)
    


class UserMedia(models.Model):
    resume = models.FileField(upload_to="resume/", null=True)
    profile_picture = models.FileField(upload_to="profile_picture/", null=True)
    uuid=models.ForeignKey(User,on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.resume:
            self.resume_file_path = self.resume.path
        else:
            self.resume_file_path = ""
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'tbl_user_media'