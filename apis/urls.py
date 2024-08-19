from django.urls import path
from .views import *


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('departments/', DepartmentListCreateView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/doctors/', DepartmentDoctorsView.as_view(), name='department-doctors'),
    path('departments/<int:pk>/patients/', DepartmentPatientsView.as_view(), name='department-patients'),
    
    path('doctors/', DoctorListCreateView.as_view(), name='doctor-list-create'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),

    path('patients/', PatientListCreateView.as_view(), name='patient-list-create'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),

    path('patient_records/', PatientRecordsListCreateView.as_view(), name='patient-records-list-create'),
    path('patient_records/<int:pk>/', PatientRecordsDetailView.as_view(), name='patient-records-detail'),




    path('doctor/profile/update/', DoctorProfileUpdateView.as_view(), name='doctor-profile-update'),
]
