from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.core.validators import RegexValidator

# Creating custom user 
class CustomUserManager(BaseUserManager):
    def create_user(self, user_id, password=None, **extra_fields):
        if not user_id:
            raise ValueError("Users must have an ID")
        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, password, **extra_fields):
        # extra_fields.setdefault('is_staff', True)
        # extra_fields.setdefault('is_superuser', True)
        # return self.create_user(user_id, password, **extra_fields)
        user = self.create_user(user_id, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class GenericUser(AbstractBaseUser, PermissionsMixin):
    # validator for 4 digits userId
    userIdValidator = RegexValidator(regex=r'^\d{4}$', message='User ID must consist of 4 digits')

    user_id = models.CharField(max_length=4, unique=True, validators=[userIdValidator])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'user_id'

    objects = CustomUserManager()

    def __str__(self):
        return self.user_id


# DEPARTMEMT MODEL - 
class Department(models.Model):

    DEPARTMENTS = (
    ('MD\'s OFFICE','md\'s Office'),
    ('HR','human resource'),
    ('ADMIN','admin'),
    ('NOC', 'noc'),
    ('SCC','scc'),
    ('MARKETING','marketing'),
    ('FACILITY','facility'),
    ('INNOVATION','innovation'),
    ('DTH','dth'),
    ('ISSD','issd'),
)

    departmentId = models.AutoField(primary_key=True, blank=False, null=False, unique=True)
    departmentName = models.CharField(max_length=50, choices=DEPARTMENTS, default='MARKETING', unique=True)

    def __str__(self):
        return self.departmentName
    

# STAFF MODEL
class Staff(models.Model):

    staffId = models.CharField(max_length=20, unique=True)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phoneNumber = PhoneNumberField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(GenericUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.firstName} {self.lastName}"
    
# VISITOR MODEL
class Visitor(models.Model):
    EXCURSION = 'Excursion'
    PERSONAL = 'Personal'
    OFFICIAL = 'Official'
    MARKETING = 'Marketing'
    REASONS = [
        (EXCURSION, 'Excursion'),
        (PERSONAL, 'Personal'),
        (OFFICIAL, 'Official'),
        (MARKETING, 'Marketing')
    ]

    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
    phoneNumber = PhoneNumberField()
    email = models.EmailField()
    organization = models.CharField(max_length=200, null=True)
    numberOfGuest = models.PositiveIntegerField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    whomToSee = models.ManyToManyField(Staff, related_name='visitors')
    reason = models.CharField(max_length=100, choices=REASONS, default=OFFICIAL)
    registrationTime = models.TimeField(default=timezone.now)
    registrationDate = models.DateField()
    isApproved = models.BooleanField(default=False)
    checkOut = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.firstName} {self.lastName} - Visiting: {[staff.__str__() for staff in self.whomToSee.all()]} REASON: {self.reason}"

# VISITORLOG MODEL   
class VisitorLog(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    checkInTime = models.TimeField()
    checkOutTime = models.TimeField(null=True, blank=True)  # Check-out time is set when the visitor leaves
    attendant = models.ForeignKey(GenericUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Visitor: {self.visitor}, Visits: {self.staff}, Check-in: {self.check_in_time}, Check-out: {self.check_out_time}"

# VISIT REQUEST MODEL - 
class VisitRequest(models.Model):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    DECLINED = 'Declined'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DECLINED, 'Declined'),
    ]

    visitor = models.ForeignKey('Visitor', on_delete=models.CASCADE)
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE)
    attendant = models.ForeignKey('Attendant', on_delete=models.CASCADE, related_name='visit_requests') # user who sends the requeat to the selected staff
    request_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=PENDING)
    feedback = models.TextField(blank=True, null=True)  # Optional field for staff to provide feedback

    def __str__(self):
        return f"Visit Request from {self.visitor} to {self.staff} - Status: {self.status}"

# 
class Attendant(models.Model):

    user = models.OneToOneField(GenericUser, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    # email = models.EmailField(unique=True)
    phone_number = PhoneNumberField()

    def __str__(self):
        return f"{self.firstName} {self.lastName}"